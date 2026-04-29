import uuid
from .models import PostVideo, PostVideoLike, PostVideoComment
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db.models import Count
from django.contrib.auth import get_user_model

User = get_user_model()

# =========================
# 🎬 フィード
# =========================
def feed(request):
    posts = (
        PostVideo.objects
        .select_related("user")
        .annotate(
            likes_total=Count("likes", distinct=True),
            user_likes=Count("user__received_likes", distinct=True)
        )
        .order_by("-created_at")
    )

    if request.user.is_authenticated:
        liked_ids = set(
            PostVideoLike.objects.filter(user=request.user)
            .values_list("post_id", flat=True)
        )
    else:
        liked_ids = set()

    return render(request, "videos/feed.html", {
        "posts": posts,
        "liked_ids": liked_ids,

        "is_feed": True,
    })


# =========================
# ⬆️ アップロード
# =========================
@login_required
def upload(request):
    if request.method == "POST":

        media = request.FILES.get("media")  # ← name変更済み前提
        media_type = request.POST.get("media_type")

        if not media:
            return render(request, "videos/upload.html", {
                "error": "ファイルを選択してください"
            })

        post = PostVideo.objects.create(
            user=request.user,
            media_type=media_type,
            caption=request.POST.get("caption")
        )

        # 🔥 分岐保存
        if media:
            if media_type == "image":
                post.image = media
            elif media_type == "video":
                post.video = media

        post.save()

        return redirect("feed")

    return render(request, "videos/upload.html")


# =========================
# ❤️ いいねトグル（シンプル拡張版）
# =========================
@require_POST
def toggle_like(request, post_id):
    post = get_object_or_404(PostVideo, id=post_id)

    # =========================
    # 🔐 ログインユーザー
    # =========================
    if request.user.is_authenticated:

        like, created = PostVideoLike.objects.get_or_create(
            user=request.user,
            post=post
        )

        if not created:
            like.delete()
            liked = False
        else:
            liked = True

        return JsonResponse({
            "liked": liked,
            "count": post.likes.count()
        })

    # =========================
    # 👤 未ログインユーザー
    # =========================
    else:
        guest_id = request.COOKIES.get("guest_id")

        if not guest_id:
            guest_id = str(uuid.uuid4())

        like, created = PostVideoLike.objects.get_or_create(
            guest_id=guest_id,
            post=post
        )

        if not created:
            like.delete()
            liked = False
        else:
            liked = True

        response = JsonResponse({
            "liked": liked,
            "count": post.likes.count()
        })

        response.set_cookie(
            "guest_id",
            guest_id,
            max_age=60 * 60 * 24 * 365,
            samesite="Lax"
        )

        return response

# =========================
# 💬 コメント取得
# =========================
def get_comments(request, post_id):
    comments = PostVideoComment.objects.filter(
        post_id=post_id
    ).select_related("user").order_by("-created_at")[:30]

    data = [
        {
            "user": c.user.username,
            "icon": c.user.get_profile_image(),
            "text": c.text,
        }
        for c in comments
    ]

    return JsonResponse({"comments": data})


# =========================
# 💬 コメント投稿
# =========================
@login_required
@require_POST
def add_comment(request, post_id):

    text = request.POST.get("text", "").strip()

    if not text:
        return JsonResponse({"error": "empty"}, status=400)

    comment = PostVideoComment.objects.create(
        user=request.user,
        post_id=post_id,
        text=text
    )

    # 🔥 高速カウント
    count = PostVideoComment.objects.filter(post_id=post_id).count()

    return JsonResponse({
        "user": request.user.username,
        "icon": request.user.get_profile_image(),
        "text": comment.text,
        "count": count
    })

# =========================
# 🔥 ユーザーフィード
# =========================
def user_video_feed(request, username):
    user = get_object_or_404(User, username=username)

    posts = PostVideo.objects.filter(user=user).order_by("-created_at")

    start = int(request.GET.get("start", 0))

    return render(request, "videos/feed.html", {
        "posts": posts,
        "start_index": start
    })