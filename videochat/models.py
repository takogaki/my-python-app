from django.conf import settings
from django.db import models
from django.contrib.auth import get_user_model
from django.utils.text import slugify
from uuid import uuid4

User = settings.AUTH_USER_MODEL


class VideoRoom(models.Model):
    is_active = models.BooleanField(default=True)
    host = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    room_slug = models.SlugField(unique=True)

    password = models.CharField(max_length=128, blank=True)

    is_live = models.BooleanField(default=False)
    is_closed = models.BooleanField(default=False)

    thumbnail = models.ImageField(
        upload_to="room_thumbnails/",
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    last_heartbeat = models.DateTimeField(
        null=True,
        blank=True
    )

    def __str__(self):
        return self.title


class JoinRequest(models.Model):
    room = models.ForeignKey(VideoRoom, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    approved = models.BooleanField(default=False)
    requested_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("room", "user")


class RoomParticipant(models.Model):
    room = models.ForeignKey(
        VideoRoom,
        on_delete=models.CASCADE,
        related_name="participants"
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="video_participations"
    )
    is_approved = models.BooleanField(default=False)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("room", "user")

    def __str__(self):
        return f"{self.user} in {self.room}"
