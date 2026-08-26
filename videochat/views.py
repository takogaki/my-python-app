from django.http import HttpResponseForbidden, JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.utils.text import slugify
from django.utils import timezone
from django.contrib import messages

from uuid import uuid4

from .utils import is_room_active, is_host_alive
from .models import VideoRoom, RoomParticipant, JoinRequest


# ==========================================================
# LIVE一覧
# ==========================================================

@login_required
def room_list(request):
    rooms = (
        VideoRoom.objects
        .filter(
            is_live=True,
            is_closed=False
        )
        .select_related("host")
        .order_by("-created_at")
    )

    for room in rooms:
        room.is_active_now = is_room_active(room)

    return render(
        request,
        "videochat/room_list.html",
        {
            "rooms": rooms
        }
    )


# ==========================================================
# LIVEルーム作成
# ==========================================================

@login_required
def start_room(request):

    if request.method == "POST":

        title = request.POST.get(
            "title",
            "配信ルーム"
        ).strip()

        password = request.POST.get(
            "password",
            ""
        ).strip()

        thumbnail = request.FILES.get(
            "thumbnail"
        )

        if not title:
            title = "配信ルーム"

        base = slugify(title) or "room"

        room_slug = (
            f"{base}-{uuid4().hex[:8]}"
        )

        room = VideoRoom.objects.create(
            host=request.user,
            title=title,
            room_slug=room_slug,
            password=password,
            is_live=True,
            is_closed=False,
            thumbnail=thumbnail,
        )

        return redirect(
            "videochat:room_start",
            room_slug=room.room_slug
        )

    return render(
        request,
        "videochat/room_create.html"
    )


# ==========================================================
# 配信者用LIVE画面
# ==========================================================

@login_required
def room_start(request, room_slug):

    room = get_object_or_404(
        VideoRoom,
        room_slug=room_slug
    )

    if room.host != request.user:
        return HttpResponseForbidden(
            "配信者のみアクセスできます"
        )

    if room.is_closed:
        return redirect(
            "videochat:room_list"
        )

    return render(
        request,
        "videochat/room_start.html",
        {
            "room": room,
            "is_host": True,
        }
    )


# ==========================================================
# LIVE視聴
# ==========================================================

@login_required
def room_join(request, room_slug):

    room = get_object_or_404(
        VideoRoom,
        room_slug=room_slug
    )

    # 終了済みLIVE
    if room.is_closed or not room.is_live:
        messages.info(
            request,
            "このLIVEは終了しています。"
        )

        return redirect(
            "videochat:room_list"
        )

    # パスワード付きLIVE
    if room.password:

        session_key = (
            f"room_auth_{room_slug}"
        )

        if not request.session.get(session_key):

            return redirect(
                "videochat:room_password",
                room_slug=room_slug
            )

    # 配信者自身の場合
    is_host = (
        request.user == room.host
    )

    # 視聴者として参加
    participant = None

    if not is_host:

        participant, created = (
            RoomParticipant.objects.get_or_create(
                room=room,
                user=request.user,
                defaults={
                    "is_approved": False
                }
            )
        )

    return render(
        request,
        "videochat/room_watch.html",
        {
            "room": room,
            "is_host": is_host,
            "participant": participant,
        }
    )


# ==========================================================
# パスワード認証
# ==========================================================

@login_required
def room_password(request, room_slug):

    room = get_object_or_404(
        VideoRoom,
        room_slug=room_slug
    )

    if room.is_closed or not room.is_live:

        messages.info(
            request,
            "このLIVEは終了しています。"
        )

        return redirect(
            "videochat:room_list"
        )

    if not room.password:

        return redirect(
            "videochat:room_join",
            room_slug=room_slug
        )

    error = None

    if request.method == "POST":

        input_password = request.POST.get(
            "password",
            ""
        )

        if input_password == room.password:

            request.session[
                f"room_auth_{room_slug}"
            ] = True

            return redirect(
                "videochat:room_join",
                room_slug=room_slug
            )

        error = "パスワードが違います。"

    return render(
        request,
        "videochat/room_password.html",
        {
            "room": room,
            "error": error,
        }
    )


# ==========================================================
# 配信者用参加者管理
# ==========================================================

@login_required
def room_manage(request, room_slug):

    room = get_object_or_404(
        VideoRoom,
        room_slug=room_slug
    )

    if room.host != request.user:

        return HttpResponseForbidden(
            "配信者のみ管理できます"
        )

    requests = (
        JoinRequest.objects
        .filter(
            room=room,
            approved=False
        )
        .select_related("user")
        .order_by("-requested_at")
    )

    participants = (
        RoomParticipant.objects
        .filter(room=room)
        .select_related("user")
        .order_by("-joined_at")
    )

    return render(
        request,
        "videochat/room_manage.html",
        {
            "room": room,
            "requests": requests,
            "participants": participants,
        }
    )


# ==========================================================
# 参加者承認
# ==========================================================

@login_required
def approve_participant(
    request,
    room_slug,
    user_id
):

    room = get_object_or_404(
        VideoRoom,
        room_slug=room_slug
    )

    if room.host != request.user:

        return HttpResponseForbidden()

    join_request = get_object_or_404(
        JoinRequest,
        room=room,
        user_id=user_id
    )

    join_request.approved = True
    join_request.save(
        update_fields=["approved"]
    )

    RoomParticipant.objects.update_or_create(
        room=room,
        user=join_request.user,
        defaults={
            "is_approved": True
        }
    )

    return redirect(
        "videochat:room_manage",
        room_slug=room_slug
    )


# ==========================================================
# LIVE終了
# ==========================================================

@login_required
@require_POST
def room_end(request, room_slug):

    room = get_object_or_404(
        VideoRoom,
        room_slug=room_slug
    )

    if room.host != request.user:

        return HttpResponseForbidden(
            "配信者のみ終了できます"
        )

    room.is_live = False
    room.is_closed = True
    room.save(
        update_fields=[
            "is_live",
            "is_closed",
        ]
    )

    return redirect(
        "videochat:room_list"
    )


# ==========================================================
# 強制終了
# ==========================================================

@login_required
@require_POST
def force_close(request, room_id):

    room = get_object_or_404(
        VideoRoom,
        id=room_id,
        host=request.user
    )

    room.is_live = False
    room.is_closed = True

    room.save(
        update_fields=[
            "is_live",
            "is_closed",
        ]
    )

    return redirect(
        "videochat:room_list"
    )


# ==========================================================
# ホストHeartbeat
# ==========================================================

@login_required
@require_POST
def room_heartbeat(request, room_slug):

    room = get_object_or_404(
        VideoRoom,
        room_slug=room_slug
    )

    if request.user != room.host:

        return JsonResponse(
            {
                "status": "forbidden"
            },
            status=403
        )

    # 現在のモデルに last_joined_at が存在するため、
    # LIVEのホスト生存確認として使用
    room.last_joined_at = timezone.now()

    room.save(
        update_fields=[
            "last_joined_at"
        ]
    )

    return JsonResponse(
        {
            "status": "ok"
        }
    )


# ==========================================================
# 参加申請
# ==========================================================

@login_required
@require_POST
def request_participation(
    request,
    room_slug
):

    room = get_object_or_404(
        VideoRoom,
        room_slug=room_slug,
        is_live=True,
        is_closed=False
    )

    if request.user == room.host:

        return JsonResponse(
            {
                "status": "host"
            }
        )

    participant, created = (
        RoomParticipant.objects.get_or_create(
            room=room,
            user=request.user,
            defaults={
                "is_approved": False
            }
        )
    )

    if participant.is_approved:

        return JsonResponse(
            {
                "status": "approved"
            }
        )

    join_request, created = (
        JoinRequest.objects.get_or_create(
            room=room,
            user=request.user
        )
    )

    if not join_request.approved:

        return JsonResponse(
            {
                "status": "requested"
            }
        )

    participant.is_approved = True
    participant.save(
        update_fields=[
            "is_approved"
        ]
    )

    return JsonResponse(
        {
            "status": "approved"
        }
    )