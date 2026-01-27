from django.http import HttpResponse
from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from .models import VideoRoom, RoomParticipant
import uuid

# テスト用
def jitsi_test(request):
    room_name = f"lino-{uuid.uuid4()}"
    url = f"https://meet.jit.si/{room_name}"
    return redirect(url)

@login_required
def room_list(request):
    rooms = VideoRoom.objects.filter(is_live=True)
    return render(request, "videochat/room_list.html", {"rooms": rooms})

# 配信開始
@login_required
def start_room(request):
    if request.method == "POST":
        room = VideoRoom.objects.create(
            host=request.user,
            title=request.POST.get("title", "配信ルーム"),
            password=request.POST.get("password", ""),
            is_live=True
        )
        return redirect("videochat:room_start", room_slug=room.room_slug)

    return render(request, "videochat/start.html")


@login_required
def room_detail(request, room_id):
    room = get_object_or_404(VideoRoom, room_id=room_id)
    return render(request, "videochat/room.html", {
        "room": room,
    })

def room_create(request):
    return render(request, "videochat/room_create.html")

@login_required
def room_join(request, room_slug):
    return HttpResponse(f"room_join OK: {room_slug}")

@login_required
def room_start(request, room_slug):
    room = get_object_or_404(VideoRoom, room_slug=room_slug)

    if room.host != request.user:
        return HttpResponseForbidden("配信者のみ開始できます")

    jitsi_url = f"https://meet.jit.si/{room.room_slug}"
    return redirect(jitsi_url)