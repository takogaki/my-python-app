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
        "display_author",   # ← ★ authorの代替
        "name",
        "parent",
        "display_reply_to", # ← ★ reply_toの代替
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

    # ===== 表示用メソッド =====

    def display_author(self, obj):
        return obj.author.username if obj.author else obj.name

    display_author.short_description = "投稿者"

    def display_reply_to(self, obj):
        return obj.reply_to.username if obj.reply_to else "-"

    display_reply_to.short_description = "返信先"