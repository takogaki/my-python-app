from django.utils import timezone
from datetime import timedelta

def is_host_alive(room):
    if not room.last_heartbeat:
        return False

    return timezone.now() - room.last_heartbeat < timedelta(seconds=40)