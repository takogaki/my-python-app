from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404
from django.contrib.auth.decorators import login_required
from django.db import models
from django.db.models import Count
from django.urls import reverse
from django.contrib.auth import get_user_model
from faker import Faker
from .forms import CommentForm, PostForm
from .models import Post, Comment, Report, CommentReport
from django.contrib import messages
from blog.models import Post
from accounts.models import SavedPost

from notifications.models import Notification
import uuid
from .utils import get_device_id


User = get_user_model()

fake = Faker()


def notify_admins(request, obj, message, admin_url_name, obj_id):
    admins = User.objects.filter(is_superuser=True)

    for admin in admins:
        Notification.objects.create(
            recipient=admin,
            actor=request.user,
            post=obj.post if hasattr(obj, "post") else obj,
            verb=message,
            target_url=reverse(admin_url_name, args=[obj_id])
        )

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
    .filter(is_hidden=False)
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
    post = get_object_or_404(Post, slug=slug, is_hidden=False)
    comment = None

    is_saved = False
    if request.user.is_authenticated:
        is_saved = SavedPost.objects.filter(
            user=request.user,
            post=post
        ).exists()

    # 親コメント
    parent_comments = (
        Comment.objects
        .filter(
            post=post,
            parent__isnull=True,
            is_hidden=False
        )
        .order_by("-posted_date")
        .prefetch_related(
            models.Prefetch(
                "replies",
                queryset=Comment.objects.filter(is_hidden=False).order_by("-posted_date")
            )
        )
    )
    
    # =======================
    # 表示名・リンク可否設定
    # =======================
    for parent_comment in parent_comments:

        # ===== 親コメント =====
        if parent_comment.author is None:
            parent_comment.display_name = parent_comment.name
            parent_comment.can_link = False

        elif parent_comment.author.is_superuser:
            parent_comment.display_name = parent_comment.author.username
            parent_comment.can_link = False

        elif not parent_comment.author.is_active:
            parent_comment.display_name = "退会ユーザー"
            parent_comment.can_link = False

        else:
            parent_comment.display_name = parent_comment.author.username
            parent_comment.can_link = True

        # ===== 返信 =====
        for reply in parent_comment.replies.all():

            # ---- 書いた人（左：A）----
            if reply.author is None:
                reply.author_display = reply.name
                reply.author_can_link = False

            elif reply.author.is_superuser:
                reply.author_display = reply.author.username
                reply.author_can_link = False

            elif not reply.author.is_active:
                reply.author_display = "退会ユーザー"
                reply.author_can_link = False

            else:
                reply.author_display = reply.author.username
                reply.author_can_link = True

            # ---- 返信先（右：B）----
            if reply.reply_to:
                if reply.reply_to.is_superuser:
                    reply.reply_to_display = reply.reply_to.username
                    reply.reply_to_can_link = False

                elif not reply.reply_to.is_active:
                    reply.reply_to_display = "退会ユーザー"
                    reply.reply_to_can_link = False

                else:
                    reply.reply_to_display = reply.reply_to.username
                    reply.reply_to_can_link = True

            else:
                # reply_to が無い場合は「親コメントの投稿者」
                reply.reply_to_display = parent_comment.display_name
                reply.reply_to_can_link = parent_comment.can_link

    # =======================
    # フォーム
    # =======================
    form = CommentForm(user=request.user)

    if request.method == "POST":
        parent_id = request.POST.get("parent_id")
        parent = Comment.objects.filter(id=parent_id).first()

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

            # 返信先ユーザー
            reply_to_id = request.POST.get("reply_to")
            if reply_to_id:
                comment.reply_to = User.objects.filter(id=reply_to_id).first()

            # 親コメント
            if parent:
                comment.parent = parent.root_parent

            comment.save()

            # =======================
            # 🔔 通知
            # =======================
            if request.user.is_authenticated:
                recipient = None

                if comment.reply_to:
                    recipient = comment.reply_to
                elif post.author:
                    recipient = post.author

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
            "is_saved": is_saved,
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


# =======================
# 投稿保存ビュー
# =======================
@login_required
def save_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    # 自分の投稿は保存させない（保険）
    if post.author == request.user:
        messages.warning(request, "自分の投稿は保存できません")
        return redirect("blog:post_detail", slug=post.slug)

    SavedPost.objects.get_or_create(
        user=request.user,
        post=post
    )

    messages.success(request, "マイページに保存しました")
    return redirect("blog:post_detail", slug=post.slug)


@login_required
def toggle_save_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    saved, created = SavedPost.objects.get_or_create(
        user=request.user,
        post=post
    )

    if not created:
        # すでに保存されていた → 解除
        saved.delete()

    return redirect("blog:post_detail", slug=post.slug)


@login_required
def report_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    # 既に通報済みなら防止（任意）
    if Report.objects.filter(post=post, reporter=request.user).exists():
        return redirect("blog:post_detail", slug=post.slug)

    # 通報作成
    Report.objects.create(
        post=post,
        reporter=request.user,
        reason=request.POST.get("reason", "")
    )

    # =========================
    # ★ ここに書く
    # =========================
    count = post.reports.count()

    if count >= 5 and post.report_notice_level < 2:
        notify_admins(post, 5)
        post.report_notice_level = 2
        post.save()

    elif count >= 3 and post.report_notice_level < 1:
        notify_admins(post, 3)
        post.report_notice_level = 1
        post.save()

    return redirect("blog:post_detail", slug=post.slug)

@login_required
def report_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)

    # 既に通報済みなら防止
    if CommentReport.objects.filter(comment=comment, reporter=request.user).exists():
        return redirect("blog:post_detail", slug=comment.post.slug)

    # 通報作成
    CommentReport.objects.create(
        comment=comment,
        reporter=request.user,
        reason=request.POST.get("reason", "")
    )

    # =========================
    # ★ 通知制御
    # =========================
    count = comment.reports.count()

    if count >= 5 and comment.report_notice_level < 2:
        notify_admins(comment, 5)
        comment.report_notice_level = 2
        comment.save()

    elif count >= 3 and comment.report_notice_level < 1:
        notify_admins(comment, 3)
        comment.report_notice_level = 1
        comment.save()

    return redirect("blog:post_detail", slug=comment.post.slug)