from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from faker import Faker
from .forms import CommentForm, PostForm
from .models import Post, Comment
import uuid

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
# トップページ
# =======================
def frontpage(request):
    posts = Post.objects.all().order_by("-posted_date")

    if request.method == "POST":
        form = PostForm(
            request.POST,
            request.FILES,
            user=request.user,  # ★ 重要
        )

        if form.is_valid():
            post = form.save(commit=False)
            post.name = post.name or fake.name()
            post.save()
            return redirect("blog:frontpage")
    else:
        form = PostForm(user=request.user)  # ★ 重要

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
            user=request.user,  # ★ 重要
        )

        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post

            anon_id = get_anonymous_id(request)

            if not comment.name:
                comment.name = f"匿名{anon_id[:4].upper()}"

            if parent:
                comment.parent = parent.root_parent
                comment.reply_to = request.POST.get("reply_to")

            comment.save()

            response = redirect("blog:post_detail", slug=slug)

            if not request.COOKIES.get("anon_id"):
                response.set_cookie(
                    "anon_id",
                    anon_id,
                    max_age=60 * 60 * 24 * 365,
                )

            return response
    else:
        form = CommentForm(user=request.user)  # ★ 重要

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