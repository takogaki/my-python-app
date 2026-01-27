from django.conf import settings
from django.db import models
from django.utils.text import slugify
from uuid import uuid4
import uuid

User = settings.AUTH_USER_MODEL


class VideoRoom(models.Model):
    host = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="video_rooms"
    )
    title      = models.CharField(max_length=100)
    room_slug  = models.SlugField(unique=True, blank=True)
    password   = models.CharField(max_length=128, blank=True)
    is_live    = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.room_slug:
            base = slugify(self.title) or uuid.uuid4().hex[:8]
            self.room_slug = f"{base}-{uuid.uuid4().hex[:6]}"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

class RoomParticipant(models.Model):
    room = models.ForeignKey(VideoRoom, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    is_approved = models.BooleanField(default=False)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("room", "user")

class JoinRequest(models.Model):
    room = models.ForeignKey(VideoRoom, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    approved = models.BooleanField(default=False)