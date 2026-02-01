from django.contrib import admin
from .models import VideoRoom
from django.utils import timezone
from datetime import timedelta


@admin.register(VideoRoom)
class VideoRoomAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "room_slug",
        "host",
        "created_at",
    )

    ordering = ("-created_at",)
    readonly_fields = ("created_at",)