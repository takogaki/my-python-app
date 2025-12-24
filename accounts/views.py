# # accounts/views.py
# from django.shortcuts import render, redirect
# from django.contrib.auth.mixins import LoginRequiredMixin
# from django.views.generic import DetailView
# from django.contrib.auth.decorators import login_required
# from django.urls import reverse_lazy
# from django.views import generic
# from .forms import CustomUserCreationForm
# from .models import CustomUser  # CustomUserをインポート
# from django.shortcuts import get_object_or_404
# from django.contrib.auth import get_user_model
# from diary.models import Page  # 日記モデルも必要

# User = get_user_model()

# @login_required  # ログインしていないとアクセスできない
# def user_list(request):
#     # ログインしているユーザー自身を除外
#     users = CustomUser.objects.exclude(pk=request.user.pk) if request.user.is_authenticated else CustomUser.objects.all()
#     return render(request, 'accounts/user_list.html', {'users': users})


# @login_required  # ログインしていないとアクセスできない
# def user_detail(request, pk):
#     user = get_object_or_404(CustomUser, pk=pk)  # CustomUserを使用
#     return render(request, 'accounts/user_detail.html', {'user': user})

# class SignUpView(generic.CreateView):
#     form_class = CustomUserCreationForm  # 自分で作成したカスタムフォーム
#     success_url = reverse_lazy('accounts:login')  # 新規登録後に/diary/にリダイレクト
#     template_name = 'accounts/signup.html'  # サインアップページのテンプレート


# def profile_view(request):
#     user = request.user  # 現在ログインしているユーザー
#     age  = user.get_age()  # 年齢を計算





# User = get_user_model()

# class UserDetailView(LoginRequiredMixin, DetailView):
#     model = User
#     template_name = "accounts/user_detail.html"
#     context_object_name = "user"

#     def get_object(self):
#         """URLのusernameからユーザーを取得"""
#         return get_object_or_404(User, username=self.kwargs['username'])

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         # 公開日記のみ取得
#         context["public_pages"] = Page.objects.filter(author=self.object, is_public=True).order_by("-page_date")
#         return context

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
from django.http import HttpResponse

from .forms import CustomUserCreationForm
from .models import CustomUser
from diary.models import Page

from django.utils.http import urlsafe_base64_decode

User = get_user_model()

# =========================
# 既存機能（完全にそのまま）
# =========================

@login_required
def user_list(request):
    users = CustomUser.objects.exclude(pk=request.user.pk) if request.user.is_authenticated else CustomUser.objects.all()
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
    template_name = 'accounts/signup.html'
    success_url = reverse_lazy('accounts:signup_done')  # ★ 即ログインさせない

    def form_valid(self, form):
        user = form.save(commit=False)
        user.is_active = False  # ★ 仮登録
        user.save()

        # ★ 認証メール送信
        token = default_token_generator.make_token(user)
        activation_url = self.request.build_absolute_uri(
            reverse('accounts:activate', args=[user.pk, token])
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
# ★ 本登録完了
# =========================

def activate(request, uid, token):
    user = get_object_or_404(User, pk=uid)

    if default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        return render(request, "accounts/activate_success.html")

    return render(request, "accounts/activate_failed.html")


def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = CustomUser.objects.get(pk=uid)
    except Exception:
        user = None

    if user and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        return redirect("accounts:login")

    return render(request, "accounts/activation_failed.html")

# =========================
# （未使用だが既存のまま残す）
# =========================

def profile_view(request):
    user = request.user
    age = user.get_age()


    # =========================
# ★ 仮登録完了画面
# =========================
def signup_done(request):
    return render(request, "accounts/signup_done.html")