from django.contrib import admin
from .models import Post, Comment
@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "video_type",
        "live_ended",
    )
    list_filter = ("video_type", "live_ended")

    fields = (
        "author",
        "body",
        "video_url",
        "video_type",
        "live_ended",
        "image",
    )
@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "post",
        "name",
        "video_type",
        "live_ended",
        "posted_date",
    )
    list_filter = ("video_type", "live_ended")
    search_fields = ("body", "name")

    fields = (
        "author",
        "body",
        "video_url",
        "video_type",
        "live_ended",
        "image",
    )
