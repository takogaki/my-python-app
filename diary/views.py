from django.shortcuts import render, get_object_or_404
from django.views.generic import View, CreateView, ListView, DetailView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from .forms import PageForm 
from .models import Page, LikeRecord
from django.contrib.auth import get_user_model
from datetime import datetime
from zoneinfo import ZoneInfo
from accounts.models import CustomUser
from django.http import JsonResponse
from django.db.models import F

User = get_user_model()


def index(request):
    return render(request, "diary/index.html")


class IndexView(View):
    def get(self, request):
        datetime_now = datetime.now(
            ZoneInfo("Asia/Tokyo")
        ).strftime("%Y年%m月%d日 %H:%M:%S")

        return render(request, "diary/index.html", {
            "datetime_now": datetime_now
        })


class PageCreateView(LoginRequiredMixin, CreateView):
    model = Page
    form_class = PageForm
    template_name = "diary/page_form.html"
    success_url = reverse_lazy("diary:page_list")

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.is_public = form.cleaned_data.get('is_public', True)
        return super().form_valid(form)


class PageListView(LoginRequiredMixin, ListView):
    model = Page
    template_name = "diary/page_list.html"
    context_object_name = "page_list"

    def get_queryset(self):
        return Page.objects.filter(
            author=self.request.user
        )


class PageDetailView(LoginRequiredMixin, DetailView):
    model = Page
    template_name = "diary/page_detail.html"
    context_object_name = "page"

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


@login_required
def like_diary(request, pk):

    page = get_object_or_404(Page, pk=pk)

    if request.method == "POST":

        page.likes = F("likes") + 1
        page.save()
        page.refresh_from_db()

        like_record, created = LikeRecord.objects.get_or_create(
            user=request.user,
            page=page
        )

        like_record.like_count += 1
        like_record.save()

        if request.user not in page.liked_users.all():
            page.liked_users.add(request.user)

        page.save()

        return JsonResponse({
            "likes": page.likes,
            "unique_users": page.unique_likes_count(),
            "user_like_count": like_record.like_count
        })

    return JsonResponse({"error": "Invalid request"}, status=400)


index = IndexView.as_view()
page_create = PageCreateView.as_view()
page_list = PageListView.as_view()
page_detail = PageDetailView.as_view()
page_update = PageUpdateView.as_view()
page_delete = PageDeleteView.as_view()