from django.http import HttpResponseForbidden
from .models import VideoRoom, RoomParticipant, JoinRequest
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.utils.text import slugify
from .models import VideoRoom
from uuid import uuid4


# テスト用（環境確認）
def jitsi_test(request):
    room_name = f"lino-{uuid4().hex[:10]}"
    return redirect(f"https://meet.jit.si/{room_name}")


@login_required
def room_list(request):
    rooms = VideoRoom.objects.filter(is_live=True, is_closed=False)
    return render(request, "videochat/room_list.html", {
        "rooms": rooms
    })


@login_required
def start_room(request):
    if request.method == "POST":
        title = request.POST.get("title", "配信ルーム")
        password = request.POST.get("password", "")

        base = slugify(title) or "room"
        room_slug = f"{base}-{uuid4().hex[:6]}"

        room = VideoRoom.objects.create(
            host=request.user,
            title=title,
            room_slug=room_slug,
            password=password,
            is_live=True,
        )

        return redirect("videochat:room_start", room_slug=room.room_slug)

    return render(request, "videochat/start.html")


@login_required
def room_start(request, room_slug):
    room = get_object_or_404(VideoRoom, room_slug=room_slug)

    if room.host != request.user:
        return HttpResponseForbidden("配信者のみ開始できます")

    room.is_live = True
    room.save()

    return redirect(f"https://meet.jit.si/{room.room_slug}")


@login_required
def room_join(request, room_slug):
    room = get_object_or_404(VideoRoom, room_slug=room_slug, is_live=True)

    # パスワードチェック
    if room.password:
        if request.method == "POST":
            if request.POST.get("password") != room.password:
                return render(request, "videochat/password.html", {
                    "room": room,
                    "error": "パスワードが違います"
                })
        else:
            return render(request, "videochat/password.html", {"room": room})

    # 申請作成（重複防止）
    join_request, created = JoinRequest.objects.get_or_create(
        room=room,
        user=request.user
    )

    return render(request, "videochat/join_requested.html", {
        "room": room,
        "already_requested": not created,
    })

@login_required
def approve_participant(request, room_slug, user_id):
    room = get_object_or_404(VideoRoom, room_slug=room_slug)

    if room.host != request.user:
        return HttpResponseForbidden()

    participant = get_object_or_404(
        RoomParticipant,
        room=room,
        user_id=user_id,
    )

    participant.is_approved = True
    participant.save()

    return redirect("videochat:room_manage", room_slug=room_slug)


@login_required
def room_manage(request, room_slug):
    room = get_object_or_404(VideoRoom, room_slug=room_slug)

    if room.host != request.user:
        return HttpResponseForbidden("配信者のみ管理できます")

    requests = JoinRequest.objects.filter(
        room=room,
        approved=False
    ).select_related("user")

    return render(request, "videochat/room_manage.html", {
        "room": room,
        "requests": requests,
    })

@login_required
def approve_participant(request, room_slug, user_id):
    room = get_object_or_404(VideoRoom, room_slug=room_slug)

    if room.host != request.user:
        return HttpResponseForbidden()

    join_request = get_object_or_404(
        JoinRequest,
        room=room,
        user_id=user_id
    )

    join_request.approved = True
    join_request.save()

    # 参加者として登録（後工程用）
    RoomParticipant.objects.get_or_create(
        room=room,
        user=join_request.user,
        defaults={"is_approved": True}
    )

    return redirect("videochat:room_manage", room_slug=room_slug)


@login_required
def room_end(request, room_slug):
    room = get_object_or_404(VideoRoom, room_slug=room_slug)

    if room.host != request.user:
        return HttpResponseForbidden()

    room.is_live = False
    room.is_closed = True
    room.save()

    return redirect("videochat:room_list")