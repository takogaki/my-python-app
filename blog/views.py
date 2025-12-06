from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from faker import Faker
from .forms import CommentForm, PostForm
from .models import Post, Comment
from django.db.models import Prefetch

fake = Faker()  # Fakerインスタンス

# フロントページビュー
def frontpage(request):
    posts = Post.objects.all().order_by('-posted_date')
    form = PostForm()  # PostFormのインスタンス化

    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.name = post.name or fake.name()  # 名前がなければランダムな名前を生成
            post.save()
            form.save()
            return redirect("blog:frontpage")  # 投稿後、frontpageにリダイレクト

    return render(request, "blog/frontpage.html", {"posts": posts, "form": form})


# 新しい投稿を作成するビュー
class PostCreateView(View):
    def get(self, request):
        form = PostForm()
        return render(request, "blog/frontpage.html", {"form": form})

    def post(self, request):
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.name = post.name or fake.name()  # 名前がなければランダムな名前を生成
            post.save()
            form.save()
            return redirect("blog:frontpage")
        return render(request, "blog/frontpage.html", {"form": form})
    

# 投稿の詳細ビュー
def post_detail(request, slug):
    post = get_object_or_404(Post, slug=slug)

    # 親コメントを新しい順で取得
    comments = Comment.objects.filter(post=post, parent__isnull=True).order_by('-posted_date')

    # 子コメントも新しい順でプリフェッチ
    parent_comments = parent_comments.prefetch_related(
        Prefetch(
            'replies',
            queryset=Comment.objects.filter(post=post).order_by('-posted_date')
        )
    )

    # コメント投稿処理
    if request.method == "POST":
        parent_id = request.POST.get("parent_comment")  # 親コメントID
        reply_to_name = request.POST.get("reply_to")  # 宛名
        parent_comment = Comment.objects.get(id=parent_id) if parent_id else None

        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.parent = parent_comment
            comment.reply_to = reply_to_name  # 宛名をセット
            comment.save()
            return redirect("blog:post_detail", slug=post.slug)  # 投稿後、詳細ページをリロード
    else:
        form = CommentForm()

    return render(request, "blog/post_detail.html", {"post": post, "comments": parent_comments, "form": form})

post_create = PostCreateView.as_view()