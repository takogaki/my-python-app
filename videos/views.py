import uuid
from .models import PostVideo, PostVideoLike, PostVideoComment, Recruit, RecruitParticipant, RecruitChatRoom, RecruitChatMessage
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db.models import Count
from django.contrib.auth import get_user_model
from accounts.utils import save_page_log
from django.contrib import messages

User = get_user_model()

# =========================
# 🎬 フィード（広告混ぜ込み版）
# =========================
def feed(request):
    # =========================
    # ページログ保存
    # =========================
    if request.user.is_authenticated:
        save_page_log(request, "feed")

    posts = (
        PostVideo.objects
        .select_related("user")
        .annotate(
            likes_total=Count("likes", distinct=True),
            user_likes=Count("user__received_likes", distinct=True)
        )
        .order_by("-created_at")
    )

    recruits = (
        Recruit.objects
        .select_related("user")
        .filter(
            is_active=True,
            status="open"
        )
        .order_by("-created_at")
    )

    # 👍 いいね済み
    if request.user.is_authenticated:
        liked_ids = set(
            PostVideoLike.objects.filter(user=request.user)
            .values_list("post_id", flat=True)
        )
    else:
        liked_ids = set()

    # =========================
    # 🔥 フィード生成（ここが核心）
    # =========================
    feed_items = []

    recruit_index = 0
    recruits = list(recruits)

    for i, post in enumerate(posts):

        # 動画投稿
        feed_items.append({
            "type": "post",
            "data": post,
        })

        # 3投稿ごとに募集を挿入
        if (
            (i + 1) % 3 == 0
            and recruit_index < len(recruits)
        ):
            feed_items.append({
                "type": "recruit",
                "data": recruits[recruit_index],
            })

            recruit_index += 1

        # 5投稿ごとに広告
        if (i + 1) % 5 == 0:
            feed_items.append({
                "type": "ad",
                "ad_type": "adsense",
            })

    return render(request, "videos/feed.html", {
        "feed_items": feed_items,
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
            "profile_url": (
                "/accounts/mypage/"
                if request.user.is_authenticated and c.user == request.user
                else f"/accounts/users/{c.user.username}/"
            ),
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
        "count": count,
        "profile_url": "/accounts/mypage/",
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

# =========================
# 🤝 募集詳細
# =========================
@login_required
def recruit_detail(request, pk):

    recruit = get_object_or_404(
        Recruit,
        pk=pk,
        is_active=True,
    )

    my_participation = None

    if request.user.is_authenticated:

        my_participation = RecruitParticipant.objects.filter(
            recruit=recruit,
            user=request.user
        ).first()

    return render(
        request,
        "videos/recruit_detail.html",
        {
            "recruit": recruit,
            "my_participation": my_participation,
        },
    )

# =========================
# 🤝 募集応募
# =========================
@login_required
@require_POST
def apply_recruit(request, pk):

    recruit = get_object_or_404(
        Recruit,
        pk=pk,
        is_active=True,
        status="open",
    )

    # 自分の募集には応募できない
    if recruit.user == request.user:
        messages.error(
            request,
            "自分の募集には応募できません。"
        )
        return redirect("recruit_detail", pk=recruit.pk)

    # すでに応募済み
    if RecruitParticipant.objects.filter(
        recruit=recruit,
        user=request.user
    ).exists():
        messages.warning(
            request,
            "すでに応募済みです。"
        )
        return redirect("recruit_detail", pk=recruit.pk)

    RecruitParticipant.objects.create(
        recruit=recruit,
        user=request.user,
        status="pending",
    )

    messages.success(
        request,
        "応募しました！"
    )

    return redirect("recruit_detail", pk=recruit.pk)

# =========================
# 👥 募集応募者一覧
# =========================
@login_required
def recruit_participants(request, pk):

    recruit = get_object_or_404(
        Recruit,
        pk=pk,
        user=request.user,
    )

    participants = (
        RecruitParticipant.objects
        .filter(recruit=recruit)
        .select_related("user")
        .order_by("created_at")
    )

    return render(
        request,
        "videos/recruit_participants.html",
        {
            "recruit": recruit,
            "participants": participants,
        },
    )


# =========================
# ✅ 応募者承認
# =========================
@login_required
@require_POST
def approve_recruit_participant(request, pk):

    participant = get_object_or_404(
        RecruitParticipant.objects.select_related(
            "recruit",
            "user",
        ),
        pk=pk,
        recruit__user=request.user,
    )

    recruit = participant.recruit

    # すでに承認済み
    if participant.status == "approved":
        messages.warning(
            request,
            "この応募者はすでに承認されています。"
        )
        return redirect(
            "recruit_participants",
            pk=recruit.pk,
        )

    # 募集が終了・中止の場合
    if recruit.status != "open":
        messages.error(
            request,
            "現在、この募集は承認できません。"
        )
        return redirect(
            "recruit_participants",
            pk=recruit.pk,
        )

    # 現在の承認人数
    approved_count = RecruitParticipant.objects.filter(
        recruit=recruit,
        status="approved",
    ).count()

    # 最大人数チェック
    if approved_count >= recruit.max_people:
        recruit.status = "full"
        recruit.save(update_fields=["status"])

        messages.error(
            request,
            "募集人数がすでに満員です。"
        )

        return redirect(
            "recruit_participants",
            pk=recruit.pk,
        )

    # 承認
    participant.status = "approved"
    participant.save(update_fields=["status", "updated_at"])

    # 承認後に満員になった場合
    new_approved_count = approved_count + 1

    if new_approved_count >= recruit.max_people:
        recruit.status = "full"
        recruit.save(update_fields=["status"])

    messages.success(
        request,
        f"{participant.user.username} さんを承認しました！"
    )

    return redirect(
        "recruit_participants",
        pk=recruit.pk,
    )


# =========================
# ❌ 応募者拒否
# =========================
@login_required
@require_POST
def reject_recruit_participant(request, pk):

    participant = get_object_or_404(
        RecruitParticipant.objects.select_related(
            "recruit",
            "user",
        ),
        pk=pk,
        recruit__user=request.user,
    )

    recruit = participant.recruit

    # すでに拒否済み
    if participant.status == "rejected":
        messages.warning(
            request,
            "この応募者はすでに拒否されています。"
        )
        return redirect(
            "recruit_participants",
            pk=recruit.pk,
        )

    participant.status = "rejected"
    participant.save(update_fields=["status", "updated_at"])

    messages.success(
        request,
        f"{participant.user.username} さんの応募を拒否しました。"
    )

    return redirect(
        "recruit_participants",
        pk=recruit.pk,
    )

# =========================
# 💬 募集チャット
# =========================
@login_required
def recruit_chat(request, pk):

    recruit = get_object_or_404(
        Recruit,
        pk=pk,
        is_active=True,
    )

    # 募集主
    is_owner = recruit.user == request.user

    # 承認済み参加者
    is_participant = RecruitParticipant.objects.filter(
        recruit=recruit,
        user=request.user,
        status="approved",
    ).exists()

    # 権限チェック
    if not is_owner and not is_participant:

        messages.error(
            request,
            "この募集チャットに参加する権限がありません。"
        )

        return redirect(
            "recruit_detail",
            pk=recruit.pk
        )

    # チャットルーム取得・作成
    room, created = RecruitChatRoom.objects.get_or_create(
        recruit=recruit
    )

    # =========================
    # 💬 メッセージ送信
    # =========================
    if request.method == "POST":

        text = request.POST.get("text", "").strip()

        if text:

            RecruitChatMessage.objects.create(
                room=room,
                user=request.user,
                text=text,
            )

        return redirect(
            "recruit_chat",
            pk=recruit.pk
        )

    # =========================
    # 💬 メッセージ取得
    # =========================
    chat_messages = room.messages.select_related(
        "user"
    ).all()

    return render(
        request,
        "videos/recruit_chat.html",
        {
            "recruit": recruit,
            "room": room,
            "chat_messages": chat_messages,
        }
    )