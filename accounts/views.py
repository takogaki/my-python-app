# accounts/views.py
import uuid, qrcode, base64
from io import BytesIO
from urllib.parse import urlencode
from django.shortcuts import render, redirect, get_object_or_404, redirect
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
from django.utils.http import urlencode, urlsafe_base64_encode, urlsafe_base64_decode, url_has_allowed_host_and_scheme
from django.utils import timezone
from datetime import date, timedelta

from diary.models import Page              # 日記
from blog.models import Post, Comment      # ブログ投稿
from videos.models import PostVideo
from accounts.models import SavedPost      # 保存した投稿
from user_messages.models import Message   # メッセージ（※名前は実物に合わせて）
from django.db.models import Count, Q, F, Exists, OuterRef
from django.utils.encoding import force_str, force_bytes
from django.utils.decorators import method_decorator
from .forms import ActivateProfileImageForm, CustomUserCreationForm, UserForm, ProfileForm, KYCForm
from notifications.models import Notification
from .models import CustomUser, UserLike, Match, VerificationLog, KYCSubmission, Footprint, Profile, TagCategory, ProfileTag, Tag, TagCategory, UserPageLog
from django.views.decorators.csrf import csrf_exempt
from accounts.utils import compatibility, profile_completion
from collections import defaultdict
from .utils import compatibility, save_page_log
from django.contrib.auth import get_user_model, login, logout
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.views.decorators.cache import never_cache
from django.contrib.auth.views import LoginView

# 広告関連
from advertisements.utils import get_random_advertisements


User = get_user_model()


# =========================
# 既存機能（そのまま）
# =========================
def user_list(request):

    users = CustomUser.objects.filter(
        is_active=True,
        is_superuser=False
    )

    # ログイン中だけ自分を除外
    if request.user.is_authenticated:
        users = users.exclude(pk=request.user.pk)

    matched_user_ids = []
    liked_user_ids = []

    # ログイン中だけ取得
    if request.user.is_authenticated:

        matches = Match.objects.filter(
            Q(user1=request.user) | Q(user2=request.user)
        )

        for match in matches:
            if match.user1 == request.user:
                matched_user_ids.append(match.user2.id)
            else:
                matched_user_ids.append(match.user1.id)

        liked_user_ids = UserLike.objects.filter(
            from_user=request.user
        ).values_list("to_user_id", flat=True)

    # =========================
    # 📢 A8net広告
    # =========================
    advertisements = get_random_advertisements("user_list")

    # =========================
    # 📢 広告をランダム順にする
    # =========================
    import random

    advertisements = get_random_advertisements("user_list")
    random.shuffle(advertisements)

    return render(request, "accounts/user_list.html", {
        "users": users,
        "matched_user_ids": matched_user_ids,
        "liked_user_ids": list(liked_user_ids),
        "advertisements": advertisements,
    })

# ========================
# 足跡リスト
# ========================
@login_required
def footprint_list(request):
    user = request.user

    # =========================
    # 🔔 足あと未読を既読化
    # =========================
    Notification.objects.filter(
        recipient=user,
        type="footprint",
        is_read=False
    ).update(
        is_read=True
    )

    # 🔥 足あと取得
    footprints = Footprint.objects.filter(
        to_user=user
    ).select_related("from_user").order_by("-created_at")

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

# =========================
# ★ ユーザープロフィール詳細ビュー
# （未ログイン閲覧対応版）
# =========================
class UserDetailView(DetailView):
    model = User
    template_name = "accounts/user_detail.html"
    context_object_name = "user"

    def get_object(self):

        user = get_object_or_404(
            User,
            username=self.kwargs["username"],
            is_superuser=False,
            is_active=True
        )

        # =========================
        # 🔥 足あと処理
        # （ログイン時のみ）
        # =========================
        if self.request.user.is_authenticated:

            if self.request.user != user:

                recent = Footprint.objects.filter(
                    from_user=self.request.user,
                    to_user=user,
                    created_at__gte=timezone.now() - timedelta(minutes=10)
                ).exists()

                if not recent:
                    Footprint.objects.update_or_create(
                        from_user=self.request.user,
                        to_user=user,
                        defaults={
                            "created_at": timezone.now()
                        }
                    )

                # =========================
                # 🔥 通知（6時間制限）
                # =========================
                recent_notify = Notification.objects.filter(
                    recipient=user,
                    actor=self.request.user,
                    type="footprint",
                    created_at__gte=timezone.now() - timedelta(hours=6)
                ).exists()

                if not recent_notify:

                    Notification.objects.create(
                        recipient=user,
                        actor=self.request.user,
                        type="footprint",
                        verb="さんがプロフィールを見ました"
                    )

        return user

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        user = self.object

        # =========================
        # ❤️ LIKE済み判定
        # =========================
        is_liked = False

        if self.request.user.is_authenticated:

            is_liked = UserLike.objects.filter(
                from_user=self.request.user,
                to_user=user
            ).exists()

        context["is_liked"] = is_liked

        # =========================
        # 🔥 プロフィール
        # =========================
        profile, _ = Profile.objects.get_or_create(
            user=user
        )

        context["profile_tags"] = (
            ProfileTag.objects
            .filter(profile=profile)
            .select_related("tag__category")
        )

        # =========================
        # 💘 相性スコア
        # （ログイン時のみ）
        # =========================
        score = None

        if self.request.user.is_authenticated:

            try:
                score = compatibility(
                    self.request.user,
                    user
                )
            except:
                score = None

        context["score"] = score

        # =========================
        # 📝 公開日記
        # =========================
        context["public_pages"] = (
            Page.objects.filter(
                author=user,
                is_public=True
            )
            .order_by("-page_date")
        )

        # =========================
        # 📰 ブログ
        # =========================
        context["blog_posts"] = (
            Post.objects.filter(
                author=user
            )
            .order_by("-posted_date")
        )

        # =========================
        # 🎥 動画
        # =========================
        context["video_posts"] = (
            PostVideo.objects.filter(
                user=user
            )
            .order_by("-created_at")
        )

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
            subject="【SPIRYTUS】本登録のご案内",
            message=f"""SPIRYTUSへの仮登録ありがとうございます。

            以下の内容で登録されています。

            ユーザー名：{user.username}
            メールアドレス：{user.email}

            ━━━━━━━━━━━━━━━━━━

            下記のリンクをクリックして、本登録を完了してください。

            {activation_url}

            ━━━━━━━━━━━━━━━━━━

            このメールに心当たりがない場合は、
            このメールを破棄してください。

            SPIRYTUS
            """,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
        )


        return super().form_valid(form)
    
# =========================
# 利用規約
# =========================
def terms(request):

    # signup=1 が付いているか
    show_signup_button = (
        request.GET.get("signup") == "1"
    )

    # 🔵 同意
    if request.method == "POST" and request.user.is_authenticated:

        request.user.agreed_terms_at = timezone.now()

        request.user.save(
            update_fields=["agreed_terms_at"]
        )

        return redirect("/")

    return render(
        request,
        "accounts/terms.html",
        {
            "show_signup_button": show_signup_button,
        }
    )
# =========================
# プライバシーポリシー
# =========================
def privacy(request):
    return render(request, "accounts/privacy.html")
# =========================
# ガイドライン
# =========================
def guideline(request):
    return render(request, "accounts/guideline.html")

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

# =========================
# ★ カスタムログイン関数（セッションリセット付き）
# =========================
class CustomLoginView(LoginView):
    template_name = "accounts/login.html"
    redirect_authenticated_user = True

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("/accounts/mypage/")
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        next_url = self.request.POST.get("next") or self.request.GET.get("next")

        # =========================
        # 🔥 安全なURLかチェック（重要）
        # =========================
        if next_url and url_has_allowed_host_and_scheme(
            url=next_url,
            allowed_hosts={self.request.get_host()},
            require_https=self.request.is_secure(),
        ):
            return next_url

        return "/accounts/mypage/"

# =========================
# ★ ログイン後リダイレクト
# =========================
def after_login_redirect(request):

    user = request.user

    # 自動最適化ON
    if user.auto_home_screen:
        screen = get_most_used_page(user)

    # 手動設定
    else:
        screen = user.home_screen
    if screen == "messages":
        return redirect("message_box")
    elif screen == "index":
        return redirect("index")
    elif screen == "mypage":
        return redirect("accounts:mypage")
    elif screen == "frontpage":
        return redirect("frontpage")
    elif screen == "roomlist":
        return redirect("room_list")
    return redirect("feed")

# =========================
# ★ 最も使われているページ取得
# =========================
def get_most_used_page(user):

    seven_days_ago = timezone.now() - timedelta(days=7)

    result = (
        UserPageLog.objects
        .filter(
            user=user,
            viewed_at__gte=seven_days_ago
        )
        .values("page_name")
        .annotate(total=Count("id"))
        .order_by("-total")
        .first()
    )

    if result:
        return result["page_name"]

    return "feed"


@login_required
def app_entry(request):

    screen = request.user.home_screen

    if screen == "messages":
        return redirect("user_messages:message_box")

    elif screen == "index":
        return redirect("index")

    elif screen == "mypage":
        return redirect("accounts:mypage")

    elif screen == "frontpage":
        return redirect("blog:frontpage")

    elif screen == "roomlist":
        return redirect("videochat:room_list")

    return redirect("feed")

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
@never_cache
@login_required
def mypage(request):
    user = request.user

    profile, _ = Profile.objects.get_or_create(user=user)

    diaries = Page.objects.filter(author=user).order_by("-page_date")
    blog_posts = Post.objects.filter(author=user).order_by("-posted_date")
    # 投稿（動画・画像）
    video_posts = PostVideo.objects.filter(user=user).order_by("-created_at") 

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
    # 管理人（superuser）からの通知は表示しない
    # =========================
    notifications = Notification.objects.filter(
        recipient=user,
        is_read=False
    ).filter(
        Q(actor__isnull=True) | Q(actor__is_superuser=False)
    ).order_by("-created_at")

    unread_count = notifications.count()

    # =========================
    # 🔔 交流メニュー未読件数
    # =========================

    base_unread = Notification.objects.filter(
        recipient=user,
        is_read=False
    ).filter(
        Q(actor__isnull=True) | Q(actor__is_superuser=False)
    )

    notification_counts = {
        "tag_match": base_unread.filter(type="tag_match").count(),
        "footprint": base_unread.filter(type="footprint").count(),
        "like": base_unread.filter(type="like").count(),
        "match": base_unread.filter(type="match").count(),
        "message": base_unread.filter(type="message").count(),
    }

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
            "video_posts": video_posts,
            "profile_tags": profile_tags,
            "messages": messages,
            "profile": profile,
            "notifications": notifications,
            "unread_count": unread_count,
            "saved_posts": saved_posts,
            "reported_posts": reported_posts,
            "reported_comments": reported_comments,
            "completion": completion,  # ← 必須
            # 🔔 追加
            "notification_counts": notification_counts,
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

# =========================
# ★ プロフィール編集ビュー（タグ処理完成版）
# =========================
@never_cache
@login_required
def profile_edit(request):

    # =========================
    # 🔥 まず必ず本人Profileをロック取得
    # =========================
    profile, _ = Profile.objects.get_or_create(user=request.user)

    if request.method == "POST":

        with transaction.atomic():

            # 🔥 ロックし直す（重要）
            profile = Profile.objects.select_for_update().get(user=request.user)

            profile_form = ProfileForm(
                request.POST,
                request.FILES,
                instance=profile
            )

            user_form = UserForm(
                request.POST,
                instance=request.user
            )

            if profile_form.is_valid() and user_form.is_valid():

                # =========================
                # user保存
                # =========================
                user = user_form.save()

                # =========================
                # profile保存
                # =========================
                profile.bio = profile_form.cleaned_data.get("bio")

                image = profile_form.cleaned_data.get("profile_image")

                # =========================
                # 🔥 default画像判定
                # =========================
                image_url = ""

                if profile.profile_image:
                    image_url = str(profile.profile_image)

                force_profile_image = (
                    not profile.profile_image
                    or "default" in image_url
                )

                # =========================
                # 🔥 未画像ユーザーは画像必須
                # =========================
                if force_profile_image and not image:

                    messages.error(
                        request,
                        "プロフィール画像を設定してください。"
                    )

                    return render(request, "accounts/profile_edit.html", {
                        "profile_form": profile_form,
                        "user_form": user_form,
                        "categories": TagCategory.objects.prefetch_related("tags").order_by("order"),
                        "completion": profile_completion(profile),
                        "selected_tags": {
                            pt.tag_id: pt.level
                            for pt in ProfileTag.objects.filter(profile=profile)
                        },
                        "force_profile_image": True,
                    })

                # =========================
                # 🔥 新画像保存
                # =========================
                if image:
                    profile.profile_image = image

                # 🔥 絶対に他ユーザーへ紐付かない保証
                profile.user_id = request.user.id

                profile.save()

                # =========================
                # 🏷 タグ処理
                # =========================

                tag_ids = request.POST.getlist("tags") or []

                # =========================
                # 🔥 削除されたタグを削除
                # =========================
                ProfileTag.objects.filter(
                    profile=profile
                ).exclude(
                    tag_id__in=tag_ids
                ).delete()


                # =========================
                # 🔥 タグ保存
                # =========================
                for tag_id in tag_ids:

                    level = request.POST.get(
                        f"level_{tag_id}",
                        2
                    )

                    profile_tag, created = ProfileTag.objects.update_or_create(
                        profile=profile,
                        tag_id=tag_id,
                        defaults={
                            "level": int(level)
                        }
                    )

                    # =========================
                    # 🔔 新しく追加されたタグだけ通知
                    # =========================
                    if created:

                        # このタグを持っている他ユーザー
                        matched_users = CustomUser.objects.filter(
                            profile__profile_tags__tag_id=tag_id,
                            is_active=True,
                            is_superuser=False,
                        ).exclude(
                            id=request.user.id
                        ).distinct()

                        for target_user in matched_users:

                            # =========================
                            # 🔥 同じ未読通知を重複作成しない
                            # =========================
                            already_exists = Notification.objects.filter(
                                recipient=target_user,
                                actor=request.user,
                                type="tag_match",
                                is_read=False,
                            ).exists()

                            if already_exists:
                                continue

                            Notification.objects.create(
                                recipient=target_user,
                                actor=request.user,
                                type="tag_match",
                                verb="さんとタグが一致しました"
                            )

                messages.success(request, "保存しました")
                return redirect("accounts:mypage")

        messages.error(request, "入力にエラーがあります")

    else:
        profile = Profile.objects.get(user=request.user)
        profile_form = ProfileForm(instance=profile)
        user_form = UserForm(instance=request.user)

    categories = TagCategory.objects.prefetch_related("tags").order_by("order")

    selected_tags = {
        pt.tag_id: pt.level
        for pt in ProfileTag.objects.filter(profile=profile)
    }

    completion = profile_completion(profile)

    # =========================
    # 🔥 未画像ユーザー判定
    # =========================
    image_url = ""

    if profile.profile_image:
        image_url = str(profile.profile_image)

    force_profile_image = (
        not profile.profile_image
        or "default" in image_url
    )

    return render(request, "accounts/profile_edit.html", {
        "profile_form": profile_form,
        "user_form": user_form,
        "categories": categories,
        "completion": completion,
        "selected_tags": selected_tags,
        "force_profile_image": force_profile_image,
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

# =========================
# ★ ログアウト
# =========================
@never_cache
def logout_view(request):

    # 🔥 完全ログアウト
    logout(request)

    # 🔥 session完全破棄
    request.session.flush()

    response = redirect("accounts:login")

    # 🔥 キャッシュ禁止
    response["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response["Pragma"] = "no-cache"
    response["Expires"] = "0"

    # 🔥 Cookie削除
    response.delete_cookie("sessionid")
    response.delete_cookie("csrftoken")

    return response


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

    # =========================
    # 🔔 タグ一致未読を既読化
    # =========================
    Notification.objects.filter(
        recipient=user,
        type="tag_match",
        is_read=False
    ).update(
        is_read=True
    )

    # =========================
    # 🔥 自分のタグ取得
    # =========================
    my_tags = ProfileTag.objects.filter(
        profile=user.profile
    ).values_list("tag_id", flat=True)

    # =========================
    # 🔥 タグ一致ユーザー
    # =========================
    if not my_tags:

        users = CustomUser.objects.none()

    else:

        users = CustomUser.objects.filter(
            profile__profile_tags__tag_id__in=my_tags,
            is_active=True,
            is_superuser=False,
        ).exclude(
            id=user.id
        ).annotate(
            common_tags=Count(
                "profile__profile_tags",
                filter=Q(
                    profile__profile_tags__tag_id__in=my_tags
                )
            )
        ).order_by(
            "-common_tags"
        ).distinct()

    # =========================
    # 🔥 マッチ済みユーザー
    # =========================
    matched_user_ids = Match.objects.filter(
        Q(user1=user) | Q(user2=user)
    ).values_list(
        "user1",
        "user2"
    )

    matched_user_ids = {
        uid
        for pair in matched_user_ids
        for uid in pair
        if uid != user.id
    }

    # =========================
    # ❤️ LIKE済み
    # =========================
    liked_user_ids = UserLike.objects.filter(
        from_user=user
    ).values_list(
        "to_user_id",
        flat=True
    )

    return render(
        request,
        "accounts/tag_users.html",
        {
            "users": users,
            "matched_user_ids": matched_user_ids,
            "liked_user_ids": liked_user_ids,
        }
    )

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

        # マッチ判定
        match_qs = Match.objects.filter(
            Q(user1=self.request.user, user2=OuterRef("pk")) |
            Q(user2=self.request.user, user1=OuterRef("pk"))
        )

        # LIKE判定
        like_qs = UserLike.objects.filter(
            from_user=self.request.user,
            to_user=OuterRef("pk")
        )

        return User.objects.exclude(
            id=self.request.user.id
        ).annotate(
            is_match=Exists(match_qs),
            is_liked=Exists(like_qs)
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        matches = Match.objects.filter(
            Q(user1=self.request.user) | Q(user2=self.request.user)
        )

        matched_user_ids = set()

        for match in matches:
            if match.user1 == self.request.user:
                matched_user_ids.add(match.user2.id)
            else:
                matched_user_ids.add(match.user1.id)

        context["matched_user_ids"] = matched_user_ids

        return context
    
# =========================
# ★ LIKE機能（重要）
# ＝========================
@login_required
def like_user(request, user_id):
    
    if request.method != "POST":
        return JsonResponse({"status": "error"})

    to_user = get_object_or_404(User, id=user_id)
    me = request.user

    if me == to_user:
        return JsonResponse({"status": "error"})

    # =========================
    # 🔥 既存LIKEチェック
    # =========================
    existing_like = UserLike.objects.filter(
        from_user=me,
        to_user=to_user
    ).first()

    # =========================
    # ❌ 既にLIKE → 取り消し
    # =========================
    if existing_like:
        existing_like.delete()

        CustomUser.objects.filter(id=to_user.id).update(
            received_likes_count=F('received_likes_count') - 1
        )

        Match.objects.filter(
            Q(user1=me, user2=to_user) |
            Q(user1=to_user, user2=me)
        ).delete()

        Notification.objects.filter(
            recipient=to_user,
            actor=me,
            type="like"
        ).delete()

        return JsonResponse({"status": "unliked"})


    # =========================
    # ✅ 新規LIKE
    # =========================
    UserLike.objects.create(
        from_user=me,
        to_user=to_user
    )

    CustomUser.objects.filter(id=to_user.id).update(
        received_likes_count=F('received_likes_count') + 1
    )

    # =========================
    # 🔥 マッチ判定
    # =========================
    is_match = UserLike.objects.filter(
        from_user=to_user,
        to_user=me
    ).exists()

    if is_match:
        user1 = min(me, to_user, key=lambda u: u.id)
        user2 = max(me, to_user, key=lambda u: u.id)

        Match.objects.get_or_create(
            user1=user1,
            user2=user2
        )

        Notification.objects.create(
            recipient=me,
            actor=to_user,
            type="match",
            verb="さんとマッチしました"
        )

        Notification.objects.create(
            recipient=to_user,
            actor=me,
            type="match",
            verb="さんとマッチしました"
        )

        request.session["matched_user"] = to_user.username

        return JsonResponse({
            "status": "match",
            "username": to_user.username
        })

    # =========================
    # 👍 LIKE通知
    # =========================
    Notification.objects.create(
        recipient=to_user,
        actor=me,
        type="like",
        verb="さんがライクしました"
    )

    return JsonResponse({"status": "liked"})

    
# like_meビュー（自分がLIKEされたユーザーのリスト）
@login_required
def liked_me(request):
    user = request.user

    # =========================
    # 🔔 ライク未読を既読化
    # =========================
    Notification.objects.filter(
        recipient=user,
        type="like",
        is_read=False
    ).update(
        is_read=True
    )

    # =========================
    # 🔥 ライクしてきたユーザー
    # =========================
    users = CustomUser.objects.filter(
        given_likes__to_user=user
    ).annotate(
        like_count=Count(
            "given_likes",
            filter=Q(given_likes__to_user=user)
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
# ★ match_resultビュー
# 相互LIKE成立 → DM可能
# =========================
@login_required
def match_result(request):
    username = request.session.pop("matched_user", None)

    if not username:
        return redirect("accounts:user_list")

    matched_user = get_object_or_404(
        CustomUser,
        username=username
    )

    me = request.user

    # =========================
    # 🔥 相互LIKE（Match）確認
    # =========================
    is_match = Match.objects.filter(
        Q(user1=me, user2=matched_user) |
        Q(user1=matched_user, user2=me)
    ).exists()

    # =========================
    # ❌ MatchしていなければDM不可
    # =========================
    if not is_match:
        return redirect(
            "accounts:user_detail",
            username=matched_user.username
        )

    # =========================
    # 💬 相互LIKE成立 → DM可能
    # =========================
    redirect_url = reverse(
        "user_messages:send_message",
        args=[matched_user.username]
    )

    return render(request, "accounts/match_result.html", {
        "user": matched_user,
        "redirect_url": redirect_url,
    })

    # =========================
    # 🔥 ここが最重要（完全修正）
    # =========================
    if not me.is_verified:
        redirect_url = reverse("accounts:kyc_submit")
    else:
        redirect_url = reverse(
            "user_messages:send_message",
            args=[matched_user.username]
        )

    return render(request, "accounts/match_result.html", {
        "user": matched_user,
        "redirect_url": redirect_url,
    })

# match_listビュー（自分がマッチしたユーザーのリスト）
@login_required
def match_list(request):
    user = request.user

    # =========================
    # 🔔 マッチ未読を既読化
    # =========================
    Notification.objects.filter(
        recipient=user,
        type="match",
        is_read=False
    ).update(
        is_read=True
    )

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

    # 既読化
    n.is_read = True
    n.save(update_fields=["is_read"])

    # =========================
    # 🔥 メッセージ通知（最優先）
    # =========================
    if n.type == "message":
        if n.actor:
            return redirect("user_messages:send_message", username=n.actor.username)
        return redirect("accounts:mypage")

    # =========================
    # ユーザー系通知
    # =========================
    if n.type in ["like", "footprint", "match"]:
        if n.actor and not n.actor.is_superuser:
            return redirect(
                "accounts:user_detail",
                username=n.actor.username
            )

        return redirect("accounts:mypage")

    # =========================
    # コメント通知
    # =========================
    if n.type == "comment" and n.post:
        return redirect("blog:post_detail", slug=n.post.slug)

    # =========================
    # fallback
    # =========================
    return redirect("accounts:mypage")