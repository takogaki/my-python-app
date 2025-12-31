from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import View, CreateView, ListView, DetailView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from .forms import PageForm 
from .models import Page, LikeRecord
from django.contrib.auth import get_user_model
from datetime import datetime
from django.utils import timezone
from zoneinfo import ZoneInfo
from accounts.models import CustomUser  # カスタムユーザーモデルをインポート
from django.http import JsonResponse

User = get_user_model()
timezone.now()  # タイムゾーン付きの現在日時を取得


def index(request):
    return render(request, "index.html")

class IndexView(View):
    def get(self, request):
        datetime_now = datetime.now(
            ZoneInfo("Asia/Tokyo")
        ).strftime("%Y年%m月%d日 %H:%M:%S")
        return render(request, "diary/index.html", {"datetime_now": datetime_now})


class PageCreateView(LoginRequiredMixin, CreateView):
    model = Page
    form_class = PageForm
    template_name = "diary/page_form.html"
    success_url = reverse_lazy("diary:page_list")

    def form_valid(self, form):
        """フォームが有効な場合にログイン中のユーザーをauthorに設定"""
        form.instance.author = self.request.user  # ログイン中のユーザーを設定
        # チェックボックスの値をフォームから取得して設定
        form.instance.is_public = form.cleaned_data.get('is_public', True)  # ここで反映

        return super().form_valid(form)


class PageListView(LoginRequiredMixin, ListView):
    model = Page
    template_name = "diary/page_list.html"
    context_object_name = "page_list"

    def get_queryset(self):
        """ログイン中のユーザーの日記のみ表示"""
        return Page.objects.filter(author=self.request.user).order_by("-page_date")


class PageDetailView(LoginRequiredMixin, DetailView):
    model = Page
    template_name = "diary/page_detail.html"
    context_object_name = "page"


class PageUpdateView(LoginRequiredMixin, UpdateView):
    model = Page
    form_class = PageForm
    template_name = "diary/page_update.html"

    def get_queryset(self):
        """ログイン中のユーザーが作成した日記のみ更新可能"""
        return Page.objects.filter(author=self.request.user)

    def get_success_url(self):
        return reverse_lazy("diary:page_detail", kwargs={"pk": self.object.pk})


class PageDeleteView(LoginRequiredMixin, DeleteView):
    model = Page
    template_name = "diary/page_confirm_delete.html"
    success_url = reverse_lazy("diary:page_list")

    def get_queryset(self):
        """ログイン中のユーザーが作成した日記のみ削除可能"""
        return Page.objects.filter(author=self.request.user)


# class UserDetailView(LoginRequiredMixin, DetailView):
#     model = CustomUser
#     template_name = "diary/user_detail.html"
#     context_object_name = "user"

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         # ユーザーの公開日記のみ取得
#         context["public_pages"] = Page.objects.filter(author=self.object, is_public=True)
#         return context


# 関数ベースビュー
@login_required
def user_diary_list(request, user_id):
    """指定されたユーザーの公開日記一覧"""
    user = get_object_or_404(CustomUser, id=user_id)
    diaries = Page.objects.filter(author=user, is_public=True)  # 公開日記のみ
    return render(request, "diary/user_diary_list.html", {"diaries": diaries, "user": user})

User = get_user_model()

class UserDetailView(DetailView):
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

@login_required
def like_diary(request, pk):
    """
    日記にいいねを付けるビュー (押すたびに増加 & ユニークユーザー管理)
    """
    page = get_object_or_404(Page, pk=pk)

    if request.method == 'POST':
        # 👍ボタンを押した回数を増やす
        page.likes += 1

        # LikeRecordを取得または作成
        like_record, created = LikeRecord.objects.get_or_create(
            user=request.user,
            page=page
        )

        # いいね回数を更新
        like_record.like_count += 1
        like_record.save()

        # ユーザーをユニークユーザーリストに追加
        if request.user not in page.liked_users.all():
            page.liked_users.add(request.user)

        # データを保存
        page.save()

        return JsonResponse({
            "likes": page.likes,  # 総 👍 回数
            "unique_users": page.unique_likes_count(),  # ユニークユーザー数
            "user_like_count": like_record.like_count  # このユーザーのいいね回数
        })

    return JsonResponse({"error": "Invalid request method."}, status=400)

    # return JsonResponse({"error": "POSTリクエストのみ受け付けます"}, status=400)

# URLConfで使用するビュー
index       = IndexView.as_view()
page_create = PageCreateView.as_view()
page_list   = PageListView.as_view()
page_detail = PageDetailView.as_view()
page_update = PageUpdateView.as_view()
page_delete = PageDeleteView.as_view()