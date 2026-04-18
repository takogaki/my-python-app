# accounts/views.py
import uuid, qrcode, base64
from io import BytesIO
from urllib.parse import urlencode
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import DetailView, ListView
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy, reverse
from django.views import generic
from django.http import JsonResponse
from django.contrib.auth import get_user_model, login, logout
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.contrib import messages
from django.conf import settings
from django.utils.http import urlencode, urlsafe_base64_encode, urlsafe_base64_decode
from django.utils import timezone
from datetime import date, timedelta
from diary.models import Page              # 日記
from blog.models import Post, Comment      # ブログ投稿
from accounts.models import SavedPost      # 保存した投稿
from user_messages.models import Message   # メッセージ（※名前は実物に合わせて）
from django.db.models import Count, Q
from django.utils.encoding import force_str, force_bytes
from django.utils.decorators import method_decorator
from .forms import ActivateProfileImageForm, CustomUserCreationForm, UserForm, ProfileForm, KYCForm
from notifications.models import Notification
from .models import CustomUser, UserLike, Match, VerificationLog, KYCSubmission, Footprint, Profile, TagCategory, ProfileTag, Tag, TagCategory # タグ関連
from django.views.decorators.csrf import csrf_exempt
from accounts.utils import compatibility, profile_completion
from collections import defaultdict
from .utils import compatibility
from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied

User = get_user_model()


# =========================
# 既存機能（そのまま）
# =========================
@login_required
def user_list(request):
    users = CustomUser.objects.filter(
        is_active=True,
        is_superuser=False
    ).exclude(pk=request.user.pk)

    # ✅ マッチ済み
    matches = Match.objects.filter(
        Q(user1=request.user) | Q(user2=request.user)
    )

    matched_user_ids = []
    for match in matches:
        if match.user1 == request.user:
            matched_user_ids.append(match.user2.id)
        else:
            matched_user_ids.append(match.user1.id)

    # ✅ LIKE済み（修正版）
    liked_user_ids = UserLike.objects.filter(
        from_user=request.user
    ).values_list("to_user_id", flat=True)

    return render(request, "accounts/user_list.html", {
        "users": users,
        "matched_user_ids": matched_user_ids,
        "liked_user_ids": list(liked_user_ids),
    })

@login_required
def user_detail(request, pk):
    user = get_object_or_404(
        CustomUser,
        pk=pk,
        is_superuser=False,
        is_active=True
    )

    # 🔥 これだけでOK
    profile, _ = Profile.objects.get_or_create(user=user)

    profile_tags = ProfileTag.objects.filter(
        profile=profile
    ).select_related("tag__category")

    # =========================
    # 足跡
    # =========================
    if request.user != user:

        Footprint.objects.update_or_create(
            from_user=request.user,
            to_user=user,
            defaults={"created_at": timezone.now()}
        )

        recent = Notification.objects.filter(
            recipient=user,
            actor=request.user,
            type="footprint",
            created_at__gte=timezone.now() - timedelta(hours=6)
        ).exists()

        if not recent:
            Notification.objects.create(
                recipient=user,
                actor=request.user,
                type="footprint",
                verb="さんがプロフィールを見ました",
                post=None
            )

    # =========================
    # 相性スコア
    # =========================
    score = compatibility(request.user, user) if request.user.is_authenticated else None

    return render(request, "accounts/user_detail.html", {
        "user": user,
        "profile_tags": profile_tags,
        "score": score,
    })

# ========================
# 足跡リスト
# ========================
@login_required
def footprint_list(request):
    user = request.user

    # 🔥 足あと取得
    footprints = Footprint.objects.filter(
        to_user=user
    ).select_related("from_user").order_by("-created_at")

    # 🔥 タグ取得
    my_tags = user.profile.tags.all()

    # 🔥 共通タグ付きでユーザー情報強化
    users_qs = CustomUser.objects.annotate(
        common_tags=Count(
            "profile__tags",
            filter=Q(profile__tags__in=my_tags)
        )
    )

    # 🔥 マッチ
    matched_pairs = Match.objects.filter(
        Q(user1=user) | Q(user2=user)
    ).values_list("user1", "user2")

    matched_user_ids = set([
        u for pair in matched_pairs for u in pair if u != user.id
    ])

    # 🔥 いいね済み
    liked_user_ids = set(
        UserLike.objects.filter(from_user=user)
        .values_list("to_user", flat=True)
    )

    return render(request, "accounts/footprint_list.html", {
        "footprints": footprints,
        "matched_user_ids": matched_user_ids,
        "liked_user_ids": liked_user_ids,
    })

class UserDetailView(LoginRequiredMixin, DetailView):
    model = User
    template_name = "accounts/user_detail.html"
    context_object_name = "user"

    def get_object(self):
        return get_object_or_404(
            User,
            username=self.kwargs["username"],
            is_superuser=False,
            is_active=True
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        user = self.object

        # 🔥 これを追加（最重要）
        profile, _ = Profile.objects.get_or_create(user=user)

        context["profile_tags"] = ProfileTag.objects.filter(
            profile=profile
        ).select_related("tag__category")

        # 既存
        context["public_pages"] = Page.objects.filter(
            author=user,
            is_public=True
        ).order_by("-page_date")

        context["blog_posts"] = Post.objects.filter(
            author=user
        ).order_by("-posted_date")

        return context


# =========================
# ★ 新規登録（メール認証付き）
# =========================
class SignUpView(generic.CreateView):
    form_class = CustomUserCreationForm
    template_name = "accounts/signup.html"
    success_url = reverse_lazy("accounts:signup_done")

    def form_valid(self, form):
        # ★ next を session に保存
        next_url = self.request.GET.get("next")
        if next_url:
            self.request.session["signup_next"] = next_url

        user = form.save(commit=False)
        user.is_active = False
        user.activation_token = uuid.uuid4()
        user.save()

        activation_url = self.request.build_absolute_uri(
            reverse(
                "accounts:activate",
                kwargs={"token": user.activation_token}
            )
        )

        send_mail(
            subject="【本登録のご案内】",
            message=f"以下のリンクをクリックしてください。\n\n{activation_url}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
        )

        return super().form_valid(form)
    
# =========================
# 利用規約
# =========================
def terms(request):

    # 🔵 既存ユーザーが同意ボタン押したとき
    if request.method == "POST" and request.user.is_authenticated:
        request.user.agreed_terms_at = timezone.now()
        request.user.save(update_fields=["agreed_terms_at"])
        return redirect("/")

    # 🟢 表示（未ログイン or 未同意ユーザー）
    return render(request, 'accounts/terms.html', {
        "is_authenticated": request.user.is_authenticated
    })

# =========================
# 仮登録完了画面
# =========================
def signup_done(request):
    return render(request, "accounts/signup_done.html")


# =========================
# 本登録（画像設定）
# =========================
def activate(request, token):
    try:
        user = CustomUser.objects.get(
            activation_token=token,
            is_active=False
        )
    except CustomUser.DoesNotExist:
        return render(request, "accounts/activate_failed.html")

    # 🔹 GET：画像選択画面
    if request.method == "GET":
        form = ProfileForm(instance=user)   # ← ★ここだけ
        return render(
            request,
            "accounts/activate_success.html",
            {"form": form}
        )

    # 🔹 POST：画像保存 → 本登録完了
    form = ProfileForm(
        request.POST,
        request.FILES,
        instance=user                     # ← ★ここだけ
    )

    if form.is_valid():
        form.save()

        user.is_active = True
        user.activation_token = None
        user.save(update_fields=["is_active", "activation_token"])

        login(request, user)

        next_url = request.session.pop("signup_next", None)
        if next_url:
            return redirect(next_url)

        return redirect("/")

    return render(
        request,
        "accounts/activate_success.html",
        {"form": form}
    )

# ========================
# ★ KYC申請（超重要）
# ========================
@login_required
def kyc_submit(request):
    user = request.user

    uid = request.GET.get("uid")
    is_qr = request.GET.get("qr") == "1"

    # =========================
    # 🔥 QRアクセス時（最重要）
    # =========================
    if is_qr:
        if str(user.id) != str(uid):

            # 🔥 今のURLをそのままnextへ
            login_url = reverse("accounts:login")
            next_url = request.get_full_path()

            messages.error(request, "別アカウントです。ログインし直してください")
            return redirect(f"{login_url}?next={next_url}")

    # =========================
    # 🔥 pendingブロック
    # =========================
    if KYCSubmission.objects.filter(user=user, status="pending").exists():
        messages.error(request, "現在確認中です。しばらくお待ちください。")
        return redirect("accounts:mypage")

    # =========================
    # 🔥 既存データ
    # =========================
    kyc = KYCSubmission.objects.filter(user=user).order_by("-created_at").first()

    # =========================
    # 🔥 QR生成
    # =========================
    qr_url = request.build_absolute_uri(
        f"/accounts/kyc/?uid={user.id}&qr=1"
    )

    qr = qrcode.make(qr_url)
    buffer = BytesIO()
    qr.save(buffer, format="PNG")
    qr_code = base64.b64encode(buffer.getvalue()).decode()

    # =========================
    # 🔥 form
    # =========================
    form = KYCForm(instance=kyc)

    # =========================
    # 🔥 POST
    # =========================
    if request.method == "POST":
        form = KYCForm(request.POST, request.FILES, instance=kyc)

        if form.is_valid():
            kyc = form.save(commit=False)
            kyc.user = user
            kyc.status = "pending"
            kyc.save()

            user.verification_status = "pending"
            user.verification_attempts += 1
            user.save(update_fields=[
                "verification_status",
                "verification_attempts"
            ])

            messages.success(request, "本人確認を送信しました。")

            if is_qr:
                return redirect("accounts:kyc_complete_mobile")

            return redirect("accounts:mypage")

    return render(request, "accounts/kyc_submit.html", {
        "form": form,
        "kyc": kyc,
        "qr_code": qr_code,
        "is_qr": is_qr,
    })

# =========================
# ★ 管理者 KYC一覧
# =========================
@login_required
def admin_kyc_list(request):
    if not request.user.is_superuser:
        return redirect("/")

    kycs = KYCSubmission.objects.select_related("user").order_by("-created_at")

    return render(request, "accounts/admin_kyc_list.html", {
        "kycs": kycs
    })


# =========================
# ★ 承認
# =========================
@login_required
def admin_kyc_approve(request, kyc_id):
    if not request.user.is_superuser:
        return redirect("/")

    kyc = get_object_or_404(KYCSubmission, id=kyc_id)

    kyc.status = "approved"
    kyc.save(update_fields=["status"])

    user = kyc.user
    user.verification_status = "verified"
    user.verified_at = timezone.now()
    user.save(update_fields=["verification_status", "verified_at"])

    messages.success(request, "承認しました")
    return redirect("accounts:admin_kyc_list")


# =========================
# ★ 却下
# =========================
@login_required
def admin_kyc_reject(request, kyc_id):
    if not request.user.is_superuser:
        return redirect("/")

    kyc = get_object_or_404(KYCSubmission, id=kyc_id)

    kyc.status = "rejected"
    kyc.save(update_fields=["status"])

    user = kyc.user
    user.verification_status = "failed"
    user.save(update_fields=["verification_status"])

    messages.error(request, "却下しました")
    return redirect("accounts:admin_kyc_list")

# =========================
# ★ KYC申請完了（スマホ専用）
# =========================
@login_required
def kyc_complete_mobile(request):
    return render(request, "accounts/kyc_complete_mobile.html")

# =========================
# ★ マイページ
# =========================
@login_required
def mypage(request):
    user = request.user

    profile, _ = Profile.objects.get_or_create(user=user)

    diaries = Page.objects.filter(author=user).order_by("-page_date")
    blog_posts = Post.objects.filter(author=user).order_by("-posted_date")

    profile_tags = ProfileTag.objects.filter(
        profile=profile
    ).select_related("tag__category")

    # =========================
    # メッセージ
    # =========================
    all_messages = (
        Message.objects
        .filter(Q(sender=user) | Q(recipient=user))
        .order_by("-sent_at")
    )

    conversations = {}
    for m in all_messages:
        other = m.recipient if m.sender == user else m.sender
        if other and other.id not in conversations:
            conversations[other.id] = m

    messages = list(conversations.values())

    # =========================
    # 保存投稿
    # =========================
    saved_posts = (
        SavedPost.objects
        .filter(user=user)
        .select_related("post")
    )

    # =========================
    # 通知
    # =========================
    notifications = Notification.objects.filter(
        recipient=user,
        is_read=False
    ).order_by("-created_at")

    unread_count = notifications.count()

    # =========================
    # 管理者用 通報
    # =========================
    reported_posts = Post.objects.none()
    reported_comments = Comment.objects.none()

    if user.is_superuser:
        reported_posts = (
            Post.objects
            .annotate(report_count=Count("reports"))
            .filter(report_count__gte=3)
            .order_by("-report_count")
        )

        reported_comments = (
            Comment.objects
            .annotate(report_count=Count("reports"))
            .filter(report_count__gte=3)
            .order_by("-report_count")
        )

    # =========================
    # ★ 完成度（ここ重要）
    # =========================
    completion = profile_completion(profile)

    return render(
        request,
        "accounts/mypage.html",
        {
            "diaries": diaries,
            "blog_posts": blog_posts,
            "profile_tags": profile_tags,
            "messages": messages,
            "profile": profile,
            "notifications": notifications,
            "unread_count": unread_count,
            "saved_posts": saved_posts,
            "reported_posts": reported_posts,
            "reported_comments": reported_comments,
            "completion": completion,  # ← 必須
        }
    )

# =========================
# ★ 管理人向けメッセージ
# =========================
@login_required
def admin_message_list(request):
    messages = Message.objects.filter(
        recipient=request.user
    ).order_by("-sent_at")

    return render(
        request,
        "accounts/admin_message_list.html",
        {"messages": messages}
    )

# =========================
# ★ 管理人向けメッセージ詳細ビュー未読 → 既読
# =========================
@login_required
def admin_message_detail(request, pk):
    message = get_object_or_404(
        Message,
        pk=pk,
        recipient=request.user
    )

    # ★ ここが未読 → 既読
    if not message.is_read:
        message.is_read = True
        message.save(update_fields=["is_read"])

    return render(
        request,
        "accounts/admin_message_detail.html",
        {"message": message}
    )



@login_required
def profile_edit(request):
    profile, created = Profile.objects.get_or_create(user=request.user)

    if profile.user != request.user:
        raise PermissionDenied("不正アクセス")

    if request.method == "POST":
        # 🔥 正しく分離
        profile_form = ProfileForm(request.POST, request.FILES, instance=profile)
        user_form = UserForm(request.POST, request.FILES, instance=request.user)

        if profile_form.is_valid() and user_form.is_valid():
            # 🔥 保存順重要（User → Profile）
            user = user_form.save()
            profile = profile_form.save(commit=False)
            profile.user = user
            profile.save()

            # =========================
            # タグ処理
            # =========================
            tag_ids = request.POST.getlist("tags")

            ProfileTag.objects.filter(profile=profile).delete()

            profile_tags = []
            for tag_id in tag_ids:
                try:
                    level = int(request.POST.get(f"level_{tag_id}", 2))
                    profile_tags.append(
                        ProfileTag(
                            profile=profile,
                            tag_id=int(tag_id),
                            level=level
                        )
                    )
                except (ValueError, TypeError):
                    continue

            ProfileTag.objects.bulk_create(profile_tags)

            return redirect("accounts:mypage")

        else:
            # 🔥 デバッグ（重要）
            print("USER FORM ERROR:", user_form.errors)
            print("PROFILE FORM ERROR:", profile_form.errors)
            print("FILES:", request.FILES)

    else:
        profile_form = ProfileForm(instance=profile)
        user_form = UserForm(instance=request.user)

    # =========================
    # タグ
    # =========================
    categories = TagCategory.objects.prefetch_related("tags").order_by("order")

    selected_tags = {
        pt.tag_id: pt.level
        for pt in ProfileTag.objects.filter(profile=profile)
    }

    completion = profile_completion(profile)

    return render(request, "accounts/profile_edit.html", {
        "profile_form": profile_form,
        "user_form": user_form,
        "categories": categories,
        "completion": completion,
        "selected_tags": selected_tags,
    })

# =========================
# ★ プロフィール画像削除ビュー（削除）
# =========================
@login_required
def profile_image_delete(request):
    profile = request.user.profile

    if profile.profile_image:
        profile.profile_image.delete(save=False)
        profile.profile_image = None
        profile.save()

    return redirect("accounts:mypage")


# ログアウト＆アカウント削除（退会）
@login_required
def withdraw_confirm(request):
    return render(request, "accounts/withdraw_confirm.html")

# 退会処理（POSTのみ）
@login_required
def withdraw_execute(request):
    if request.method == "POST":
        user = request.user
        logout(request)
        user.delete()
        return redirect("diary:index")

    return redirect("accounts:withdraw_confirm")


# =========================
# ★ タグでユーザーを絞り込むビュー
# =========================
@login_required
def users_by_tag(request, tag_id):

    users = CustomUser.objects.filter(
        profile__profile_tags__tag_id=tag_id,
        is_active=True,
        is_superuser=False
    ).exclude(id=request.user.id).distinct()

    # 🔥 マッチ取得
    matches = Match.objects.filter(
        Q(user1=request.user) | Q(user2=request.user)
    )

    matched_user_ids = []
    for match in matches:
        if match.user1 == request.user:
            matched_user_ids.append(match.user2.id)
        else:
            matched_user_ids.append(match.user1.id)

    # 🔥 LIKE済み
    liked_user_ids = UserLike.objects.filter(
        from_user=request.user
    ).values_list("to_user_id", flat=True)

    # =========================
    # 🔥 タグ一致がない場合
    # =========================
    if not users.exists():

        fallback_users = CustomUser.objects.filter(
            is_active=True,
            is_superuser=False
        ).exclude(id=request.user.id)[:50]

        users = sorted(
            fallback_users,
            key=lambda u: compatibility(request.user, u),
            reverse=True
        )

        empty_message = "同じタグのユーザーはいません。おすすめユーザーを表示しています"

    else:
        users = sorted(
            users,
            key=lambda u: compatibility(request.user, u),
            reverse=True
        )

        empty_message = None

    return render(request, "accounts/users_by_tag.html", {
        "users": users,
        "matched_user_ids": matched_user_ids,
        "liked_user_ids": list(liked_user_ids),
        "empty_message": empty_message,
    })

# =========================
# ★ タグ完全一致ユーザービュー（タグマッチング）
# =========================
@login_required
def tag_match_users(request):
    user = request.user

    my_tags = user.profile.tags.all()

    if not my_tags.exists():
        users = CustomUser.objects.none()
    else:
        users = CustomUser.objects.filter(
            profile__tags__in=my_tags
        ).exclude(
            id=user.id
        ).annotate(
            common_tags=Count("profile__tags")
        ).order_by(
            "-common_tags"
        ).distinct()

    # 🔥 ここ追加（超重要）
    matched_user_ids = Match.objects.filter(
        Q(user1=user) | Q(user2=user)
    ).values_list("user1", "user2")

    matched_user_ids = set([
        u for pair in matched_user_ids for u in pair if u != user.id
    ])

    liked_user_ids = UserLike.objects.filter(
        from_user=user
    ).values_list("to_user", flat=True)

    return render(request, "accounts/tag_users.html", {
        "users": users,
        "matched_user_ids": matched_user_ids,
        "liked_user_ids": liked_user_ids,
    })

# =========================
# エラー時、管理人宛てにメッセージ送信
# =========================
@login_required
def contact_eden(request):
    try:
        admin_user = User.objects.get(username="eden")
    except User.DoesNotExist:
        return render(request, "accounts/contact_error.html")

    if request.method == "POST":
        content = request.POST.get("content")

        Message.objects.create(
            sender=request.user,
            recipient=admin_user,
            content=content,
            is_important=True,
        )

        # ② 管理人にメールを送る
        send_mail(
            subject="【Lino】管理人宛てメッセージが届きました",
            message=(
                f"送信者：{request.user.username}\n\n"
                f"{content}"
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[admin_user.email],
        )

        messages.success(request, "管理人にメッセージを送信しました")

        # ③ 送信完了ページへ
        return redirect("accounts:contact_eden_done")

    return render(request, "accounts/contact_eden.html")

@login_required
def contact_eden_done(request):
    return render(request, "accounts/contact_eden_done.html")




# 404エラーページから管理人宛てにメッセージ送信（匿名）
def contact_eden_public(request):
    try:
        admin_user = User.objects.get(username="eden")
    except User.DoesNotExist:
        return render(request, "accounts/contact_error.html")

    if request.method == "POST":
        content = request.POST.get("content", "")

        Message.objects.create(
            sender=None,  # ← 匿名
            recipient=admin_user,
            content=f"[404ページから]\n\n{content}",
            is_important=True,
        )

        send_mail(
            subject="【Lino】404ページから連絡がありました",
            message=content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[admin_user.email],
        )

        return render(request, "accounts/contact_eden_done.html")

    return redirect("/")


# matting用のユーザーリストビュー（自分以外全員表示）
@method_decorator(login_required, name="dispatch")
class UserListView(ListView):
    model = User
    template_name = "accounts/user_list.html"
    context_object_name = "users"

    def get_queryset(self):
        # 自分以外のユーザーを表示
        return User.objects.exclude(id=self.request.user.id)
    
def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)

    matches = Match.objects.filter(
        Q(user1=self.request.user) | Q(user2=self.request.user)
    )

    match_users = []
    for match in matches:
        if match.user1 == self.request.user:
            match_users.append(match.user2)
        else:
            match_users.append(match.user1)

    context["match_users"] = match_users
    return context

# =========================
# ★ LIKE機能（重要）
# ＝========================
@login_required
def like_user(request, user_id):
    if request.method != "POST":
        return JsonResponse({"status": "error"})

    to_user = get_object_or_404(User, id=user_id)

    if request.user == to_user:
        return JsonResponse({"status": "error"})

    # =========================
    # LIKE作成
    # =========================
    like, created = UserLike.objects.get_or_create(
        from_user=request.user,
        to_user=to_user
    )

    # =========================
    # マッチ判定（←ここを常にやる）
    # =========================
    is_match = UserLike.objects.filter(
        from_user=to_user,
        to_user=request.user
    ).exists()

    if is_match:
        user1 = min(request.user, to_user, key=lambda u: u.id)
        user2 = max(request.user, to_user, key=lambda u: u.id)

        Match.objects.get_or_create(
            user1=user1,
            user2=user2
        )

        # 通知
        Notification.objects.create(
            recipient=request.user,
            actor=to_user,
            type="match",
            verb="さんとマッチしました"
        )

        Notification.objects.create(
            recipient=to_user,
            actor=request.user,
            type="match",
            verb="さんとマッチしました"
        )

        request.session["matched_user"] = to_user.username

        return JsonResponse({
            "status": "match",
            "username": to_user.username
        })

    # =========================
    # 新規ライク時だけ通知
    # =========================
    if created:
        Notification.objects.create(
            recipient=to_user,
            actor=request.user,
            type="like",
            verb="さんがライクしました"
        )

    return JsonResponse({"status": "liked"})


    
# like_meビュー（自分がLIKEされたユーザーのリスト）
@login_required
def liked_me(request):
    user = request.user

    # =========================
    # 🔥 ライクしてきたユーザー（最適化）
    # =========================
    users = CustomUser.objects.filter(
        likes_sent__to_user=user
    ).annotate(
        # 🔥 「この人が自分に送ったライク数」
        like_count=Count(
            "likes_sent",
            filter=Q(likes_sent__to_user=user)
        )
    ).order_by("-like_count", "-last_login").distinct()

    # =========================
    # 🔥 マッチユーザーID（最適化）
    # =========================
    match_user_ids = set(
        Match.objects.filter(
            Q(user1=user) | Q(user2=user)
        ).values_list("user1_id", "user2_id")
    )

    # flatten（超スマート）
    match_user_ids = {
        uid for pair in match_user_ids for uid in pair
    }

    match_user_ids.discard(user.id)

    return render(request, "accounts/liked_me.html", {
        "users": users,
        "match_user_ids": match_user_ids,
    })

# =========================
# match_resultビュー（LIKEした相手が自分をLIKEしてたときの結果表示）
# =========================
@login_required
def match_result(request):
    username = request.session.pop("matched_user", None)

    if not username:
        return redirect("accounts:user_list")

    user = get_object_or_404(CustomUser, username=username)

    return render(request, "accounts/match_result.html", {
        "user": user
    })


# match_listビュー（自分がマッチしたユーザーのリスト）
def match_list(request):
    user = request.user

    matches = Match.objects.filter(
        Q(user1=user) | Q(user2=user)
    )

    users = []
    for match in matches:
        if match.user1 == user:
            users.append(match.user2)
        else:
            users.append(match.user1)

    return render(request, "accounts/match_list.html", {
        "users": users
    })


@login_required
def notification_read(request, id):
    n = get_object_or_404(Notification, id=id, recipient=request.user)

    n.is_read = True
    n.save(update_fields=["is_read"])

    # ユーザー系通知
    if n.type in ["like", "footprint", "match"]:
        if n.actor:
            return redirect("accounts:user_detail", username=n.actor.username)

    # コメント通知（今後拡張用）
    if n.type == "comment" and n.post:
        return redirect("blog:post_detail", slug=n.post.slug)

    return redirect("accounts:mypage")