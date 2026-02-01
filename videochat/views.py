from django.http import HttpResponseForbidden, JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.utils.text import slugify
from django.contrib import messages
from django.utils import timezone
from .utils import is_room_active
from .models import VideoRoom, RoomParticipant, JoinRequest
from .utils import is_host_alive
from uuid import uuid4


# テスト用（環境確認）
def jitsi_test(request):
    room_name = f"lino-{uuid4().hex[:10]}"
    return redirect(f"https://meet.jit.si/{room_name}")


@login_required
@require_POST
def room_heartbeat(request, room_slug):
    room = get_object_or_404(VideoRoom, room_slug=room_slug)

    # ホストのみ
    if request.user != room.host:
        return JsonResponse({"status": "forbidden"}, status=403)

    room.last_heartbeat = timezone.now()
    room.save(update_fields=["last_heartbeat"])

    return JsonResponse({"status": "ok"})


@login_required
def room_list(request):
    rooms = VideoRoom.objects.filter(
        is_live=True,
        is_closed=False
    ).order_by("-created_at")

    for room in rooms:
        room.is_active_now = is_room_active(room)

    return render(request, "videochat/room_list.html", {
        "rooms": rooms
    })

@login_required
def start_room(request):
    if request.method == "POST":
        title = request.POST.get("title", "配信ルーム")
        password = request.POST.get("password", "")
        thumbnail = request.FILES.get("thumbnail")

        base = slugify(title) or "room"
        room_slug = f"{base}-{uuid4().hex[:6]}"

        room = VideoRoom.objects.create(
            host=request.user,
            title=title,
            room_slug=room_slug,
            password=password,
            is_live=True,
            thumbnail=thumbnail,
        )

        return redirect("videochat:room_start", room_slug=room.room_slug)

    return render(request, "videochat/start.html")


@login_required
def room_start(request, room_slug):
    room = get_object_or_404(VideoRoom, room_slug=room_slug)

    if room.host != request.user:
        return HttpResponseForbidden("配信者のみ開始できます")

    room.is_live = True
    room.is_closed = False
    room.save()

    return render(request, "videochat/room_start.html", {
        "room": room
    })



@login_required
def room_join(request, room_slug):
    room = get_object_or_404(VideoRoom, room_slug=room_slug)

    unclosed_room = VideoRoom.objects.filter(
        host=request.user,
        is_live=True,
        is_closed=False
    ).exclude(id=room.id).first()

    # Jitsi を開こうとした事実は必ず記録する
    request.session["has_opened_jitsi"] = True

    if unclosed_room:
        return render(
            request,
            "videochat/join_redirect.html",
            {
                "room": room,
                "unclosed_room": unclosed_room,
            }
        )

    return redirect(f"https://meet.jit.si/{room.room_slug}")

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
        return HttpResponseForbidden("配信者のみ終了できます")

    room.is_live = False
    room.is_closed = True
    room.save()

    # 終了したら必ずフラグを消す
    request.session.pop("has_opened_jitsi", None)

    return redirect("videochat:room_list")

@login_required
def force_close(request, room_id):
    room = get_object_or_404(VideoRoom, id=room_id, host=request.user)

    room.is_live = False
    room.is_closed = True
    room.save()

    # 強制終了でも必ずフラグを消す
    request.session.pop("has_opened_jitsi", None)

    return redirect("videochat:room_list")