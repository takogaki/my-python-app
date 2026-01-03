from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404
from django.contrib.auth.decorators import login_required
from faker import Faker
from .forms import CommentForm, PostForm
from .models import Post, Comment
from django.db.models import Count
import uuid
from .utils import get_device_id

fake = Faker()


# =======================
# 匿名ID
# =======================
def get_anonymous_id(request):
    anon_id = request.COOKIES.get("anon_id")
    if not anon_id:
        anon_id = uuid.uuid4().hex
    return anon_id


# =======================
# 端末一意ID取得（cookie）
# =======================
def get_device_id(request):
    device_id = request.COOKIES.get("device_id")
    if not device_id:
        device_id = uuid.uuid4().hex
    return device_id



# =======================
# トップページ
# =======================
def frontpage(request):
    posts = (
        Post.objects
        .all()
        .annotate(comment_count=Count("comments"))
        .order_by("-posted_date")
    )

    if request.method == "POST":
        form = PostForm(
            request.POST,
            request.FILES,
            user=request.user,
        )

        if form.is_valid():
            post = form.save(commit=False)

            device_id = None

            if request.user.is_authenticated:
                post.author = request.user
                post.name = request.user.username
            else:
                device_id = get_device_id(request)
                post.name = f"未ログイン-{device_id[:6]}"

            post.save()

            response = redirect("blog:frontpage")

            if device_id and not request.COOKIES.get("device_id"):
                response.set_cookie(
                    "device_id",
                    device_id,
                    max_age=60 * 60 * 24 * 365,
                )

            return response

    else:
        form = PostForm(user=request.user)

    return render(
        request,
        "blog/frontpage.html",
        {
            "posts": posts,
            "form": form,
        },
    )

# =======================
# 投稿詳細 + コメント
# =======================
def post_detail(request, slug):
    post = get_object_or_404(Post, slug=slug)

    parent_comments = Comment.objects.filter(
        post=post, parent__isnull=True
    ).order_by("-posted_date")

    if request.method == "POST":
        parent_id = request.POST.get("parent_id")
        parent = Comment.objects.get(id=parent_id) if parent_id else None

        form = CommentForm(
            request.POST,
            request.FILES,
            parent=parent,
            user=request.user,
        )

        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post

            # =========================
            # ★ ここが修正の核心
            # =========================
            device_id = None  # ← 必ず最初に定義する

            if request.user.is_authenticated:
                comment.name = request.user.username
            else:
                device_id = get_device_id(request)
                comment.name = f"未ログイン-{device_id[:6]}"

            if parent:
                comment.parent = parent.root_parent
                comment.reply_to = parent.name

            comment.save()

            response = redirect("blog:post_detail", slug=slug)

            if device_id and not request.COOKIES.get("device_id"):
                response.set_cookie(
                    "device_id",
                    device_id,
                    max_age=60 * 60 * 24 * 365,
                )

            return response
    else:
        form = CommentForm(user=request.user)

    return render(
        request,
        "blog/post_detail.html",
        {
            "post": post,
            "parent_comments": parent_comments,
            "form": form,
        },
    )


# =======================
# 投稿作成（URLに残す場合）
# =======================
def post_create(request):
    if request.method == "POST":
        form = PostForm(request.POST, user=request.user)
        if form.is_valid():
            form.save()
            return redirect("blog:frontpage")
    else:
        form = PostForm(user=request.user)

    return render(request, "blog/post_form.html", {"form": form})