from django.conf import settings
from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now

class Room(models.Model):
    host       = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='hosted_rooms')
    room_id    = models.CharField(max_length=100, unique=True)
    room_key   = models.CharField(max_length=100, blank=True, null=True)  # 鍵の管理
    is_private = models.BooleanField(default=False)
    start_time = models.DateTimeField()
    end_time   = models.DateTimeField(null=True, blank=True)

class RoomParticipant(models.Model):
    room      = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='participants')
    user      = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    joined_at = models.DateTimeField(auto_now_add=True)
    is_host   = models.BooleanField(default=False)  # 新しいフィールドを追加