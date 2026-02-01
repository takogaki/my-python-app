# videochat/context_processors.py
from videochat.models import VideoRoom

def unclosed_room_warning(request):
    if not request.user.is_authenticated:
        return {}

    if not request.session.get("has_opened_jitsi"):
        return {}

    room = VideoRoom.objects.filter(
        host=request.user,
        is_live=True,
        is_closed=False
    ).first()

    return {"unclosed_room": room}