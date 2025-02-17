# accounts/views.py
from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import DetailView
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.views import generic
from .forms import CustomUserCreationForm
from .models import CustomUser  # CustomUserをインポート
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from diary.models import Page  # 日記モデルも必要

User = get_user_model()

@login_required  # ログインしていないとアクセスできない
def user_list(request):
    # ログインしているユーザー自身を除外
    users = CustomUser.objects.exclude(pk=request.user.pk) if request.user.is_authenticated else CustomUser.objects.all()
    return render(request, 'accounts/user_list.html', {'users': users})


@login_required  # ログインしていないとアクセスできない
def user_detail(request, pk):
    user = get_object_or_404(CustomUser, pk=pk)  # CustomUserを使用
    return render(request, 'accounts/user_detail.html', {'user': user})

class SignUpView(generic.CreateView):
    form_class = CustomUserCreationForm  # 自分で作成したカスタムフォーム
    success_url = reverse_lazy('accounts:login')  # 新規登録後に/diary/にリダイレクト
    template_name = 'accounts/signup.html'  # サインアップページのテンプレート


def profile_view(request):
    user = request.user  # 現在ログインしているユーザー
    age  = user.get_age()  # 年齢を計算





User = get_user_model()

class UserDetailView(LoginRequiredMixin, DetailView):
    model = User
    template_name = "accounts/user_detail.html"
    context_object_name = "user"

    def get_object(self):
        """URLのusernameからユーザーを取得"""
        return get_object_or_404(User, username=self.kwargs['username'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # 公開日記のみ取得
        context["public_pages"] = Page.objects.filter(author=self.object, is_public=True).order_by("-page_date")
        return context