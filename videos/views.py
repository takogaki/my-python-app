import uuid
from .models import PostVideo, PostVideoLike, PostVideoComment, Recruit, RecruitParticipant, RecruitChatRoom, RecruitChatMessage, RecruitChatRead
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, Http404
from django.views.decorators.http import require_POST
from django.db.models import Count
from django.contrib.auth import get_user_model
from accounts.utils import save_page_log
from django.contrib import messages

# 広告関連
from advertisements.utils import get_random_advertisements


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
    # 📢 広告取得
    # =========================
    advertisements = get_random_advertisements("feed")


    # =========================
    # 🔥 フィード生成
    # =========================
    feed_items = []

    recruit_index = 0
    ad_index = 0

    recruits = list(recruits)

    for i, post in enumerate(posts):

        # =========================
        # 🎬 動画投稿
        # =========================
        feed_items.append({
            "type": "post",
            "data": post,
        })

        # =========================
        # 🤝 3投稿ごとに募集
        # =========================
        if (
            (i + 1) % 3 == 0
            and recruit_index < len(recruits)
        ):
            feed_items.append({
                "type": "recruit",
                "data": recruits[recruit_index],
            })

            recruit_index += 1

        # =========================
        # 📢 5投稿ごとに広告
        # =========================
        if (i + 1) % 5 == 0:

            if advertisements:

                ad = advertisements[
                    ad_index % len(advertisements)
                ]

                feed_items.append({
                    "type": "ad",
                    "data": ad,
                })

                ad_index += 1

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
# 🤝 新規募集作成
# =========================

@login_required
def recruit_create(request):

    if request.method == "POST":

        title = request.POST.get("title", "").strip()
        category = request.POST.get("category", "").strip()
        description = request.POST.get("description", "").strip()
        place = request.POST.get("place", "").strip()
        prefecture = request.POST.get("prefecture", "").strip()
        start_time = request.POST.get("start_time") or None
        end_time = request.POST.get("end_time") or None
        expires_at = request.POST.get("expires_at") or None
        max_people = request.POST.get("max_people", "2")
        target_gender = request.POST.get("target_gender", "all")
        industry = request.POST.get("industry", "").strip()
        latitude = request.POST.get("latitude")
        longitude = request.POST.get("longitude")

        # =========================
        # 📷 募集写真
        # =========================

        recruit_image = request.FILES.get("image")

        # =========================
        # 必須項目チェック
        # =========================

        if not title:
            messages.error(
                request,
                "募集タイトルを入力してください。"
            )
            return redirect("recruit_create")

        if not category:
            messages.error(
                request,
                "カテゴリを選択してください。"
            )
            return redirect("recruit_create")

        # =========================
        # 最大人数チェック
        # =========================

        try:
            max_people = int(max_people)

            if max_people < 1:
                raise ValueError

        except (TypeError, ValueError):

            messages.error(
                request,
                "募集人数は1人以上で設定してください。"
            )

            return redirect("recruit_create")

        # =========================
        # 🤝 募集作成
        # =========================

        recruit = Recruit.objects.create(
            user=request.user,
            category=category,
            title=title,
            description=description,
            place=place,
            prefecture=prefecture,
            start_time=start_time,
            end_time=end_time,
            expires_at=expires_at,
            max_people=max_people,
            target_gender=target_gender,
            industry=industry,
            latitude=latitude or None,
            longitude=longitude or None,

            # 📷 写真
            image=recruit_image,

            status="open",
            is_active=True,
        )

        messages.success(
            request,
            "募集を作成しました！"
        )

        return redirect(
            "recruit_detail",
            pk=recruit.pk
        )

    return render(
        request,
        "videos/recruit_create.html",
        {
            "category_choices": Recruit.CATEGORY_CHOICES,
            "gender_choices": Recruit.GENDER_CHOICES,
        },
    )

# =========================
# 🤝 募集編集
# =========================
@login_required
def recruit_edit(request, pk):

    recruit = get_object_or_404(
        Recruit,
        pk=pk,
        user=request.user,
    )

    # 終了・中止した募集は編集不可
    if recruit.status in ["closed", "cancel"]:
        messages.error(
            request,
            "終了または中止した募集は編集できません。"
        )
        return redirect(
            "recruit_detail",
            pk=recruit.pk
        )

    if request.method == "POST":

        title = request.POST.get("title", "").strip()
        category = request.POST.get("category", "").strip()
        description = request.POST.get("description", "").strip()
        place = request.POST.get("place", "").strip()
        prefecture = request.POST.get("prefecture", "").strip()
        start_time = request.POST.get("start_time") or None
        end_time = request.POST.get("end_time") or None
        expires_at = request.POST.get("expires_at") or None
        max_people = request.POST.get("max_people", "2")

        target_gender = request.POST.get(
            "target_gender",
            "all"
        )

        industry = request.POST.get(
            "industry",
            ""
        ).strip()

        latitude = request.POST.get("latitude")
        longitude = request.POST.get("longitude")

        # =========================
        # 📷 募集画像
        # =========================

        image = request.FILES.get("image")


        # =========================
        # バリデーション
        # =========================

        if not title:
            messages.error(
                request,
                "募集タイトルを入力してください。"
            )
            return redirect(
                "recruit_edit",
                pk=recruit.pk
            )


        if not category:
            messages.error(
                request,
                "カテゴリを選択してください。"
            )
            return redirect(
                "recruit_edit",
                pk=recruit.pk
            )


        try:

            max_people = int(max_people)

            if max_people < 1:
                raise ValueError

        except (TypeError, ValueError):

            messages.error(
                request,
                "募集人数は1人以上で設定してください。"
            )

            return redirect(
                "recruit_edit",
                pk=recruit.pk
            )


        # =========================
        # 👥 現在の承認人数より
        # 少ない人数には変更不可
        # =========================

        if max_people < recruit.approved_count:

            messages.error(
                request,
                f"現在すでに{recruit.approved_count}人が"
                "参加確定しているため、"
                "募集人数を減らせません。"
            )

            return redirect(
                "recruit_edit",
                pk=recruit.pk
            )


        # =========================
        # 💾 募集情報更新
        # =========================

        recruit.title = title
        recruit.category = category
        recruit.description = description
        recruit.place = place
        recruit.prefecture = prefecture
        recruit.start_time = start_time
        recruit.end_time = end_time
        recruit.expires_at = expires_at
        recruit.max_people = max_people
        recruit.target_gender = target_gender
        recruit.industry = industry


        # =========================
        # 📍 GPS更新
        # =========================

        recruit.latitude = latitude or None
        recruit.longitude = longitude or None


        # =========================
        # 📷 画像更新
        #
        # 新しい画像が選択された場合だけ変更
        # 選択されなければ現在の画像を維持
        # =========================

        if image:

            recruit.image = image


        # =========================
        # 👥 人数変更による状態調整
        # =========================

        if recruit.approved_count >= recruit.max_people:

            recruit.status = "full"

        else:

            recruit.status = "open"


        # =========================
        # 保存
        # =========================

        recruit.save()


        messages.success(
            request,
            "募集内容を更新しました。"
        )


        return redirect(
            "recruit_detail",
            pk=recruit.pk
        )


    return render(
        request,
        "videos/recruit_edit.html",
        {
            "recruit": recruit,
            "category_choices": Recruit.CATEGORY_CHOICES,
            "gender_choices": Recruit.GENDER_CHOICES,
        },
    )


# =========================
# 🛑 募集終了
# =========================
@login_required
@require_POST
def close_recruit(request, pk):

    recruit = get_object_or_404(
        Recruit,
        pk=pk,
        user=request.user,
    )

    # すでに終了
    if recruit.status == "closed":
        messages.warning(
            request,
            "この募集はすでに終了しています。"
        )
        return redirect(
            "recruit_management"
        )

    # 中止済み
    if recruit.status == "cancel":
        messages.warning(
            request,
            "中止された募集は「終了」に変更できません。"
            "再開してから終了してください。"
        )
        return redirect(
            "recruit_management"
        )

    recruit.status = "closed"
    recruit.is_active = False

    recruit.save(
        update_fields=[
            "status",
            "is_active",
            "updated_at",
        ]
    )

    messages.success(
        request,
        "募集を終了しました。"
    )

    return redirect(
        "recruit_management"
    )

# =========================
# ❌ 募集中止
# =========================
@login_required
@require_POST
def cancel_recruit(request, pk):

    recruit = get_object_or_404(
        Recruit,
        pk=pk,
        user=request.user,
    )

    if recruit.status in ["closed", "cancel"]:

        messages.warning(
            request,
            "この募集はすでに終了しています。"
        )

        return redirect(
            "recruit_detail",
            pk=recruit.pk
        )

    # =========================
    # 応募者処理
    # =========================
    participant_action = request.POST.get(
        "participant_action",
        "keep",
    )

    if participant_action == "reset":

        # 応募者をキャンセル扱い
        RecruitParticipant.objects.filter(
            recruit=recruit,
        ).update(
            status="cancelled"
        )

        recruit.cancel_keep_participants = False

        message = (
            "募集を中止しました。"
            "応募者はリセットされました。"
        )

    else:

        # 応募者をそのまま保持
        recruit.cancel_keep_participants = True

        message = (
            "募集を中止しました。"
            "応募者情報を保持しています。"
        )

    # =========================
    # 募集を中止
    # =========================
    recruit.status = "cancel"
    recruit.is_active = False

    recruit.save(
        update_fields=[
            "status",
            "is_active",
            "cancel_keep_participants",
            "updated_at",
        ]
    )

    messages.success(
        request,
        message,
    )

    return redirect(
        "recruit_detail",
        pk=recruit.pk
    )

# =========================
# 🔄 募集再開
# =========================
@login_required
@require_POST
def reopen_recruit(request, pk):

    recruit = get_object_or_404(
        Recruit,
        pk=pk,
        user=request.user,
        status="cancel",
    )

    # =========================
    # 応募者をリセットした中止だった場合
    # =========================
    if not recruit.cancel_keep_participants:

        RecruitParticipant.objects.filter(
            recruit=recruit,
        ).update(
            status="cancelled"
        )

    # =========================
    # 募集再開
    # =========================
    recruit.status = "open"
    recruit.is_active = True

    recruit.save(
        update_fields=[
            "status",
            "is_active",
            "updated_at",
        ]
    )

    # =========================
    # メッセージ
    # =========================
    if recruit.cancel_keep_participants:

        messages.success(
            request,
            "募集を再開しました。"
            "以前の応募者情報を保持しています。"
        )

    else:

        messages.success(
            request,
            "募集を再開しました。"
            "以前の応募者はリセットされ、新たに応募を受け付けます。"
        )

    return redirect(
        "recruit_management"
    )

# =========================
# 🤝 募集詳細
# =========================
@login_required
def recruit_detail(request, pk):

    # まず募集そのものを取得
    recruit = get_object_or_404(
        Recruit,
        pk=pk,
    )

    # =========================
    # 他ユーザーは非公開募集を見られない
    # =========================
    if recruit.user != request.user and not recruit.is_active:
        raise Http404

    # =========================
    # 自分の応募状況
    # =========================
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

    # =========================
    # 募集主
    # =========================
    is_owner = recruit.user == request.user

    # =========================
    # 承認済み参加者
    # =========================
    is_participant = RecruitParticipant.objects.filter(
        recruit=recruit,
        user=request.user,
        status="approved",
    ).exists()

    # =========================
    # 🔐 権限チェック
    # =========================
    if not is_owner and not is_participant:

        messages.error(
            request,
            "この募集チャットに参加する権限がありません。"
        )

        return redirect(
            "recruit_detail",
            pk=recruit.pk
        )

    # =========================
    # 💬 チャットルーム取得・作成
    # =========================
    room, created = RecruitChatRoom.objects.get_or_create(
        recruit=recruit
    )

    # =========================
    # 💬 メッセージ送信
    # =========================
    if request.method == "POST":

        text = request.POST.get(
            "text",
            ""
        ).strip()

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

    # =========================
    # 🔔 最後のメッセージを取得
    # =========================
    last_message = (
        room.messages
        .order_by("-created_at")
        .first()
    )

    # =========================
    # 🔥 このユーザーの既読位置を更新
    # =========================
    if last_message:

        RecruitChatRead.objects.update_or_create(
            room=room,
            user=request.user,
            defaults={
                "last_read_message": last_message,
            }
        )

    return render(
        request,
        "videos/recruit_chat.html",
        {
            "recruit": recruit,
            "room": room,
            "chat_messages": chat_messages,
        }
    )


@login_required
def recruit_management(request):

    # =========================
    # 自分が作成した募集
    # =========================
    my_recruits = (
        Recruit.objects
        .filter(
            user=request.user,
        )
        .order_by("-created_at")
    )

    # =========================
    # 🔔 募集チャット未読数を付与
    # =========================
    for recruit in my_recruits:

        recruit.unread_count = get_recruit_unread_count(
            recruit,
            request.user
        )

    # =========================
    # 自分が応募した募集
    # =========================
    my_applications = (
        RecruitParticipant.objects
        .filter(
            user=request.user,
        )
        .select_related(
            "recruit",
            "recruit__user",
        )
        .order_by("-created_at")
    )

    return render(
        request,
        "videos/recruit_management.html",
        {
            "my_recruits": my_recruits,
            "my_applications": my_applications,
        },
    )

def get_recruit_unread_count(recruit, user):

    if not user.is_authenticated:
        return 0

    try:
        room = RecruitChatRoom.objects.get(
            recruit=recruit
        )
    except RecruitChatRoom.DoesNotExist:
        return 0

    read_state = RecruitChatRead.objects.filter(
        room=room,
        user=user,
    ).first()

    queryset = RecruitChatMessage.objects.filter(
        room=room,
    ).exclude(
        user=user,
    )

    if read_state and read_state.last_read_message_id:

        queryset = queryset.filter(
            created_at__gt=
            read_state.last_read_message.created_at
        )

    return queryset.count()