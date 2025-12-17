from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from faker import Faker
from .forms import CommentForm, PostForm
from .models import Post, Comment
from django.db.models import Prefetch
from .forms import PostForm  # ← forms.py がある前提
import uuid



fake = Faker()

def get_anonymous_id(request):
    anon_id = request.COOKIES.get("anon_id")
    if not anon_id:
        anon_id = uuid.uuid4().hex
    return anon_id

def get_anonymous_name(request):
    anon_id = get_anonymous_id(request)
    return f"匿名{anon_id[:4].upper()}"


def frontpage(request):
    posts = Post.objects.all().order_by('-posted_date')

    if request.method == "POST":
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.name = post.name or fake.name()
            post.save()
            return redirect("blog:frontpage")
    else:
        form = PostForm()

    return render(request, "blog/frontpage.html", {
        "posts": posts,
        "form": form
    })


# class PostCreateView(View):
#     def get(self, request):
#         form = PostForm(request.POST, request.FILES)
#         return render(request, "blog/frontpage.html", {"form": form})

#     def post(self, request):
#         form = PostForm(request.POST)
#         if form.is_valid():
#             post = form.save(commit=False)
#             post.name = post.name or fake.name()
#             post.save()
#             return redirect("blog:frontpage")
#         return render(request, "blog/frontpage.html", {"form": form})



# ✨ 返信フォーム生成
def get_comment_form(parent=None):
    return CommentForm(parent=parent)



# ✨ 投稿の詳細（コメント付き）
# views.py
def post_detail(request, slug):
    post = get_object_or_404(Post, slug=slug)

    parent_comments = Comment.objects.filter(
        post=post,
        parent__isnull=True
    ).order_by("-posted_date")

    if request.method == "POST":
        parent_id = request.POST.get("parent_id")
        parent = Comment.objects.get(id=parent_id) if parent_id else None

        form = CommentForm(request.POST, request.FILES)

        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post

            anon_id = get_anonymous_id(request)

            # 名前未入力なら匿名名
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

