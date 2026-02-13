# accounts/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import DetailView
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy, reverse
from django.views import generic
from django.http import JsonResponse
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.contrib import messages
from django.conf import settings
from django.utils.http import urlencode
from django.contrib.auth import login
from django.contrib.auth import logout

from diary.models import Page              # 日記
from blog.models import Post, Comment      # ブログ投稿
from accounts.models import SavedPost
from user_messages.models import Message   # メッセージ（※名前は実物に合わせて）
from django.db.models import Count

from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_str, force_bytes

from .forms import ActivateProfileImageForm
from .forms import CustomUserCreationForm
from .forms import ProfileForm
from notifications.models import Notification

from .models import CustomUser
from diary.models import Page

import uuid

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

    return render(request, "accounts/user_list.html", {"users": users})

@login_required
def user_detail(request, pk):
    user = get_object_or_404(
        CustomUser,
        pk=pk,
        is_superuser=False,
        is_active=True
    )
    return render(request, "accounts/user_detail.html", {"user": user})

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
        context["public_pages"] = Page.objects.filter(
            author=self.object,
            is_public=True
        ).order_by("-page_date")

        context["blog_posts"] = Post.objects.filter(
                author=self.object
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
# ★ マイページ
# =========================
@login_required
def mypage(request):
    user = request.user

    diaries = Page.objects.filter(author=user).order_by("-page_date")
    blog_posts = Post.objects.filter(author=user).order_by("-posted_date")
    messages = Message.objects.filter(recipient=user)

    saved_posts = (
        SavedPost.objects
        .filter(user=request.user)
        .select_related("post")
    )

    notifications = Notification.objects.filter(
        recipient=user,
        is_read=False
    ).order_by("-created_at")

    # =========================
    # ★ 管理者用 通報一覧
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

    return render(
        request,
        "accounts/mypage.html",
        {
            "diaries": diaries,
            "blog_posts": blog_posts,
            "messages": messages,
            "profile": user,
            "notifications": notifications,
            "saved_posts": saved_posts,
            "reported_posts": reported_posts,
            "reported_comments": reported_comments,
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
# ★ マイページ　ユーザーネーム編集ビュー（編集）
# =========================
@login_required
def profile_edit(request):
    user = request.user

    if request.method == "POST":
        form = ProfileForm(
            request.POST,
            request.FILES,
            instance=user
        )
        if form.is_valid():
            form.save()
            return redirect("accounts:mypage")
    else:
        form = ProfileForm(instance=user)

    return render(
        request,
        "accounts/profile_edit.html",
        {"form": form}
    )

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

@login_required
def withdraw_execute(request):
    if request.method == "POST":
        user = request.user
        logout(request)
        user.delete()
        return redirect("diary:index")

    return redirect("accounts:withdraw_confirm")


# エラー時、管理人宛てにメッセージ送信
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