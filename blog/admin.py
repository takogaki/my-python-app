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
        "author",
        "name",
        "parent",
        "reply_to",
        "posted_date",
    )

    list_filter = ("posted_date",)
    search_fields = ("body", "name", "author__username")

    fields = (
        "post",
        "author",
        "name",
        "parent",
        "reply_to",
        "body",
        "video_url",
        "image",
    )

    readonly_fields = ("posted_date",)