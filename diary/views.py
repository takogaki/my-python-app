from django.shortcuts import render, get_object_or_404
from django.views.generic import View, CreateView, ListView, DetailView, UpdateView, DeleteView
from django.views.decorators.http import require_POST
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from .forms import PageForm 
from .models import Page, LikeRecord, GuestLikeRecord, SiteNotice, SiteNoticeRead
from django.contrib.auth import get_user_model
from datetime import datetime
from zoneinfo import ZoneInfo
from accounts.models import CustomUser
from django.http import Http404, JsonResponse
from django.db.models import F
from accounts.utils import save_page_log
import uuid
from django.db import transaction
from django.contrib import messages

User = get_user_model()


class IndexView(View):
    def get(self, request):
        if request.user.is_authenticated:
            save_page_log(request, "index")

        datetime_now = datetime.now(
            ZoneInfo("Asia/Tokyo")
        ).strftime("%Y年%m月%d日 %H:%M:%S")

        # ==========================================
        # 🔔 すべてのお知らせ
        # ==========================================
        all_notices = SiteNotice.objects.all().order_by(
            "-published_at"
        )

        # ==========================================
        # 🔔 未読のお知らせ
        # ==========================================
        active_notices = SiteNotice.objects.filter(
            is_active=True
        ).order_by("-published_at")

        if request.user.is_authenticated:

            read_notice_ids = SiteNoticeRead.objects.filter(
                user=request.user
            ).values_list(
                "notice_id",
                flat=True
            )

            notices = active_notices.exclude(
                id__in=read_notice_ids
            )

        else:

            read_notice_ids = request.session.get(
                "read_site_notice_ids",
                []
            )

            notices = active_notices.exclude(
                id__in=read_notice_ids
            )

        return render(
            request,
            "diary/index.html",
            {
                "datetime_now": datetime_now,
                "notices": notices,
                "all_notices": all_notices,
            }
        )
    


@require_POST
def mark_site_notices_read(request):
    try:
        import json

        data = json.loads(
            request.body.decode("utf-8")
        )

        notice_ids = data.get("notice_ids", [])

    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse(
            {"success": False},
            status=400
        )

    if not isinstance(notice_ids, list):
        return JsonResponse(
            {"success": False},
            status=400
        )

    # ==========================================
    # 🔔 ログインユーザー
    # ==========================================
    if request.user.is_authenticated:

        notices = SiteNotice.objects.filter(
            id__in=notice_ids
        )

        for notice in notices:
            SiteNoticeRead.objects.get_or_create(
                user=request.user,
                notice=notice
            )

    # ==========================================
    # 🔔 未ログインユーザー
    # ==========================================
    else:

        current_read_ids = request.session.get(
            "read_site_notice_ids",
            []
        )

        current_read_ids = set(
            int(x) for x in current_read_ids
        )

        for notice_id in notice_ids:
            try:
                current_read_ids.add(
                    int(notice_id)
                )
            except (TypeError, ValueError):
                continue

        request.session["read_site_notice_ids"] = list(
            current_read_ids
        )

        request.session.modified = True

    return JsonResponse(
        {"success": True}
    )

class PageCreateView(LoginRequiredMixin, CreateView):
    model = Page
    form_class = PageForm
    template_name = "diary/page_form.html"
    success_url = reverse_lazy("diary:page_list")

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.is_public = form.cleaned_data.get('is_public', True)

        response = super().form_valid(form)

        messages.success(
            self.request,
            "投稿しました。"
        )

        return response

class PageListView(LoginRequiredMixin, ListView):
    model = Page
    template_name = "diary/page_list.html"
    context_object_name = "page_list"

    def get_queryset(self):
        return Page.objects.filter(
            author=self.request.user
        )


class PageDetailView(DetailView):
    model = Page
    template_name = "diary/page_detail.html"
    context_object_name = "page"

    def get_object(self):

        page = get_object_or_404(
            Page,
            pk=self.kwargs["pk"]
        )

        # 公開日記
        if page.is_public:
            return page

        # 非公開日記は本人だけ
        if self.request.user.is_authenticated and page.author == self.request.user:
            return page

        raise Http404()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["previous_url"] = self.request.META.get("HTTP_REFERER")
        return context


class PageUpdateView(LoginRequiredMixin, UpdateView):
    model = Page
    form_class = PageForm
    template_name = "diary/page_update.html"

    def get_queryset(self):
        return Page.objects.filter(author=self.request.user)

    def form_valid(self, form):

        if self.request.POST.get("picture-clear"):
            if form.instance.picture:
                form.instance.picture.delete(save=False)
            form.instance.picture = None

        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("diary:page_detail", kwargs={"pk": self.object.pk})
    
class PageDeleteView(LoginRequiredMixin, DeleteView):
    model = Page
    template_name = "diary/page_confirm_delete.html"
    success_url = reverse_lazy("diary:page_list")

    def get_queryset(self):
        return Page.objects.filter(author=self.request.user)


@login_required
def user_diary_list(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)

    diaries = Page.objects.filter(
        author=user,
        is_public=True
    )

    return render(request, "diary/user_diary_list.html", {
        "diaries": diaries,
        "user": user
    })


class UserDetailView(DetailView):
    model = User
    template_name = "accounts/user_detail.html"
    context_object_name = "user"

    def get_object(self):
        return get_object_or_404(
            User,
            username=self.kwargs['username']
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["public_pages"] = Page.objects.filter(
            author=self.object,
            is_public=True
        )

        return context



@transaction.atomic
def like_diary(request, pk):

    if request.method != "POST":
        return JsonResponse(
            {"error": "Invalid request"},
            status=400
        )

    # ログインユーザーのみ
    if not request.user.is_authenticated:
        return JsonResponse(
            {
                "error": "ログインが必要です"
            },
            status=401
        )

    # 対象の日記をロック
    page = get_object_or_404(
        Page.objects.select_for_update(),
        pk=pk
    )

    # 自分自身の日記にはいいね不可
    if page.author == request.user:
        return JsonResponse(
            {
                "error": "自分の日記にはいいねできません"
            },
            status=403
        )

    # すでにいいね済みか確認
    like_record = LikeRecord.objects.filter(
        user=request.user,
        page=page
    ).first()

    # すでにいいね済み
    if like_record:

        return JsonResponse({
            "likes": page.likes,
            "unique_users": page.liked_users.count(),
            "user_like_count": 1,
            "already_liked": True
        })

    # 初回いいねを記録
    LikeRecord.objects.create(
        user=request.user,
        page=page,
        like_count=1
    )

    # 総いいね数を1増加
    page.likes += 1
    page.save(update_fields=["likes"])

    # ユーザーを登録
    page.liked_users.add(request.user)

    return JsonResponse({
        "likes": page.likes,
        "unique_users": page.liked_users.count(),
        "user_like_count": 1,
        "already_liked": False
    })

class PublicDiaryListView(ListView):

    model = Page

    template_name = "diary/public_diary_list.html"

    context_object_name = "page_list"

    paginate_by = 20

    def get_queryset(self):

        return Page.objects.filter(
            is_public=True,
            author__is_active=True
        ).select_related(
            "author"
        ).order_by("-created_at")

index = IndexView.as_view()
page_create = PageCreateView.as_view()
page_list = PageListView.as_view()
page_detail = PageDetailView.as_view()
page_update = PageUpdateView.as_view()
page_delete = PageDeleteView.as_view()
public_diary_list = PublicDiaryListView.as_view()