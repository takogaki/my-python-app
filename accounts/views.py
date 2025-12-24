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
from django.conf import settings

from django.utils.http import (
    urlsafe_base64_encode,
    urlsafe_base64_decode
)
from django.utils.encoding import force_bytes

from .forms import CustomUserCreationForm
from .models import CustomUser
from diary.models import Page

User = get_user_model()

# =========================
# 既存機能（完全にそのまま）
# =========================

@login_required
def user_list(request):
    users = CustomUser.objects.exclude(pk=request.user.pk)
    return render(request, 'accounts/user_list.html', {'users': users})


@login_required
def user_detail(request, pk):
    user = get_object_or_404(CustomUser, pk=pk)
    return render(request, 'accounts/user_detail.html', {'user': user})


class UserDetailView(LoginRequiredMixin, DetailView):
    model = User
    template_name = "accounts/user_detail.html"
    context_object_name = "user"

    def get_object(self):
        return get_object_or_404(User, username=self.kwargs['username'])

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
        user = form.save(commit=False)
        user.is_active = False   # 仮登録
        user.save()

        # uid + token 作成
        uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)

        activation_url = self.request.build_absolute_uri(
            reverse("accounts:activate", args=[uidb64, token])
        )

        send_mail(
            subject="【本登録のご案内】",
            message=f"""
以下のリンクをクリックして登録を完了してください。

{activation_url}

※このメールに心当たりがない場合は破棄してください。
""",
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[user.email],
        )

        return super().form_valid(form)


# =========================
# ★ 本登録（これ1つだけ）
# =========================

def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()

        messages.success(request, "アカウントが有効化されました。ログインしてください。")
        return redirect("accounts:login")

    return render(request, "accounts/activate_failed.html")


# =========================
# ★ 仮登録完了画面
# =========================

def signup_done(request):
    return render(request, "accounts/signup_done.html")