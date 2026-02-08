# videochat/context_processors.py
from videochat.models import VideoRoom

def unclosed_room_warning(request):
    if not request.user.is_authenticated:
        return {}

    room = VideoRoom.objects.filter(
        host=request.user,
        is_live=True,
        is_closed=False
    ).order_by("-created_at").first()

    if not room:
        # 🔥 フラグも掃除する
        request.session.pop("has_opened_jitsi", None)
        return {}

    return {"unclosed_room": room}