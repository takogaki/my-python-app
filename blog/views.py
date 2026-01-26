from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404
from django.contrib.auth.decorators import login_required
from faker import Faker
from .forms import CommentForm, PostForm
from .models import Post, Comment
from django.db.models import Count
from notifications.models import Notification
from django.urls import reverse
import uuid
from .utils import get_device_id
from django.contrib.auth import get_user_model

User = get_user_model()

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

    # =======================
    # コメント・返信のリンク可否フラグ
    # =======================
    for comment in parent_comments:
        comment.can_link = bool(
            comment.author
            and comment.author.is_active
            and not comment.author.is_superuser
        )

    for reply in comment.replies.all():
        reply.can_link = bool(
            reply.reply_to
            and reply.reply_to.is_active
            and not reply.reply_to.is_superuser
        )

    form = CommentForm(user=request.user)

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

            device_id = None

            if request.user.is_authenticated:
                comment.author = request.user
                comment.name = request.user.username
            else:
                device_id = get_device_id(request)
                comment.name = f"未ログイン-{device_id[:6]}"

            # 🔑 reply_to（User）をセット
            reply_to_id = request.POST.get("reply_to")
            if reply_to_id:
                comment.reply_to = User.objects.filter(id=reply_to_id).first()

            # 🔑 親コメント
            if parent:
                comment.parent = parent.root_parent

            comment.save()

            # =======================
            # 🔔 通知（recipient が存在する場合のみ）
            # =======================
            if request.user.is_authenticated:
                recipient = None

                # 返信なら「返信先ユーザ」
                if comment.reply_to:
                    recipient = comment.reply_to

                # 通常コメントなら「投稿者」
                elif post.author:
                    recipient = post.author

                # 自分自身への通知は送らない
                if recipient and recipient != request.user:
                    Notification.objects.create(
                        recipient=recipient,
                        actor=request.user,
                        post=post,
                        verb=f"{request.user.username} さんがコメントしました",
                        target_url=(
                            reverse("blog:post_detail", args=[post.slug])
                            + f"#comment-{comment.id}"
                        ),
                    )

            response = redirect("blog:post_detail", slug=slug)

            if device_id and not request.COOKIES.get("device_id"):
                response.set_cookie("device_id", max_age=60 * 60 * 24 * 365)

            return response

    return render(
        request,
        "blog/post_detail.html",
        {
            "post": post,
            "parent_comments": parent_comments,
            "form": form,
        }
    )

# =======================
# 投稿作成（URLに残す場合）
# =======================
def post_create(request):
    if request.method == "POST":
        form = PostForm(request.POST, user=request.user)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user   # ★ これが必須
            post.name = request.user.username  # 表示名も揃えるなら
            form.save()
            return redirect("blog:frontpage")
    else:
        form = PostForm(user=request.user)

    return render(request, "blog/post_form.html", {"form": form})



@login_required
def end_live(request, slug):
    post = get_object_or_404(Post, slug=slug, author=request.user)

    if request.method == "POST":
        post.live_ended = True
        post.save()

    return redirect("blog:post_detail", slug=post.slug)



@login_required
def delete_post(request, slug):
    post = get_object_or_404(Post, slug=slug, author=request.user)

    if request.method == "POST":
        post.delete()

    return redirect("accounts:mypage")



@login_required
def delete_comment(request, pk):
    comment = get_object_or_404(Comment, pk=pk)

    # 本人チェック（超重要）
    if comment.post.author != request.user:
        return redirect("accounts:mypage")

    if request.method == "POST":
        comment.delete()

    return redirect("accounts:mypage")