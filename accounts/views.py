# accounts/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import DetailView
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy, reverse
from django.views import generic
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.contrib import messages
from django.conf import settings
from django.utils.http import urlencode
from django.contrib.auth import login

from diary.models import Page              # 日記
from blog.models import Post               # ブログ投稿
from user_messages.models import Message   # メッセージ（※名前は実物に合わせて）

from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_str, force_bytes

from .forms import CustomUserCreationForm
from .forms import ProfileImageForm

from .models import CustomUser
from diary.models import Page

import uuid

User = get_user_model()

# =========================
# 既存機能（そのまま）
# =========================

@login_required
def user_list(request):
    users = CustomUser.objects.exclude(pk=request.user.pk)
    return render(request, "accounts/user_list.html", {"users": users})


@login_required
def user_detail(request, pk):
    user = get_object_or_404(CustomUser, pk=pk)
    return render(request, "accounts/user_detail.html", {"user": user})


class UserDetailView(LoginRequiredMixin, DetailView):
    model = User
    template_name = "accounts/user_detail.html"
    context_object_name = "user"

    def get_object(self):
        return get_object_or_404(User, username=self.kwargs["username"])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["public_pages"] = Page.objects.filter(
            author=self.object,
            is_public=True
        ).order_by("-page_date")
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

    # 🔹 GET：画像入力画面を表示するだけ
    if request.method == "GET":
        form = ProfileImageForm(instance=user.profile)
        return render(
            request,
            "accounts/activate_success.html",
            {"form": form}
        )

    # 🔹 POST：画像保存 → 本登録完了
    form = ProfileImageForm(
        request.POST,
        request.FILES,
        instance=user.profile
    )

    if form.is_valid():
        form.save()

        # 本登録確定
        user.is_active = True
        user.activation_token = None
        user.save(update_fields=["is_active", "activation_token"])

        login(request, user)

        next_url = request.session.pop("signup_next", None)
        if next_url:
            return redirect(next_url)

        return redirect("accounts:signup_done")

    # ❌ バリデーションエラー
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
    messages = Message.objects.filter(recipient=request.user)

    return render(request, "accounts/mypage.html", {
        "diaries": diaries,
        "blog_posts": blog_posts,
        "messages": messages,
        "profile": user,
    })

def mypage(request):
    user_obj = request.user
    return render(request, "accounts/mypage.html", {
        "user_obj": user_obj,
    })