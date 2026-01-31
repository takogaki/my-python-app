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
        "is_active",
        "host_alive",
        "last_heartbeat",
        "created_at",
    )

    list_filter = ("is_active",)
    search_fields = ("room_slug", "host__username")
    ordering = ("-created_at",)

    readonly_fields = (
        "room_slug",
        "host",
        "created_at",
        "last_heartbeat",
    )

    actions = ["force_close_rooms"]

    def force_close_rooms(self, request, queryset):
        queryset.update(is_active=False, is_live=False, is_closed=True)

    force_close_rooms.short_description = "選択したルームを強制終了"

    def host_alive(self, obj):
        if not obj.last_heartbeat:
            return False
        return timezone.now() - obj.last_heartbeat < timedelta(seconds=40)

    host_alive.boolean = True
    host_alive.short_description = "ホスト生存"