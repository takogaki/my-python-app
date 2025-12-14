from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from faker import Faker
from .forms import CommentForm, PostForm
from .models import Post, Comment
from django.db.models import Prefetch
from .forms import PostForm  # ← forms.py がある前提


fake = Faker()


def frontpage(request):
    posts = Post.objects.all().order_by('-posted_date')
    form = PostForm()

    if request.method == "POST":
        # 投稿フォームだけを処理する
        if "create_post" in request.POST:
            form = PostForm(request.POST)
            if form.is_valid():
                post = form.save(commit=False)
                post.name = post.name or fake.name()
                post.save()
                return redirect("blog:frontpage")

        # 投稿フォーム以外の POST は無視
        return redirect("blog:frontpage")

    return render(request, "blog/frontpage.html", {"posts": posts, "form": form})



class PostCreateView(View):
    def get(self, request):
        form = PostForm()
        return render(request, "blog/frontpage.html", {"form": form})

    def post(self, request):
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.name = post.name or fake.name()
            post.save()
            return redirect("blog:frontpage")
        return render(request, "blog/frontpage.html", {"form": form})



# ✨ 返信フォーム生成
def get_comment_form(parent=None):
    return CommentForm(parent=parent)



# ✨ 投稿の詳細（コメント付き）
def post_detail(request, slug):
    post = get_object_or_404(Post, slug=slug)

    # 親コメント
    parent_comments = Comment.objects.filter(
        post=post,
        parent__isnull=True
    ).order_by('posted_date').prefetch_related('replies__replies')

    # コメント投稿処理
    if request.method == "POST":
        parent_id = request.POST.get("parent_id")
        parent = Comment.objects.get(id=parent_id) if parent_id else None

        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.parent = parent
            comment.save()
            return redirect("blog:post_detail", slug=slug)
    else:
        form = CommentForm()

    return render(request, "blog/post_detail.html", {
        "post": post,
        "parent_comments": parent_comments,
        "form": form,
    })


def post_create(request):
    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("post_list")  # 適宜変更
    else:
        form = PostForm()
    return render(request, "blog/post_form.html", {"form": form})

