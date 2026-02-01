from django.utils import timezone
from datetime import timedelta

def is_host_alive(room):
    if not room.last_heartbeat:
        return False
    return timezone.now() - room.last_heartbeat < timedelta(seconds=40)

def is_room_active(room):
    if room.is_closed:
        return False

    if room.last_joined_at:
        return timezone.now() - room.last_joined_at < timedelta(hours=6)

    return False