from django.contrib import admin
from .models import PostVideo, PostVideoLike, PostVideoComment, PostVideoSave


# =========================
# 🎬 投稿
# =========================
@admin.register(PostVideo)
class PostVideoAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "media_type", "created_at", "like_count_display")
    list_filter = ("media_type", "created_at")
    search_fields = ("user__username", "caption")
    ordering = ("-created_at",)

    def like_count_display(self, obj):
        return obj.likes.count()
    like_count_display.short_description = "いいね数"


# =========================
# ❤️ いいね
# =========================
@admin.register(PostVideoLike)
class PostVideoLikeAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "post", "created_at")
    search_fields = ("user__username",)
    list_filter = ("created_at",)


# =========================
# 💬 コメント
# =========================
@admin.register(PostVideoComment)
class PostVideoCommentAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "post", "short_text", "created_at")
    search_fields = ("user__username", "text")
    list_filter = ("created_at",)

    def short_text(self, obj):
        return obj.text[:20]  # 長すぎ防止
    short_text.short_description = "コメント"


# =========================
# 🔖 保存
# =========================
@admin.register(PostVideoSave)
class PostVideoSaveAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "post", "created_at")
    search_fields = ("user__username",)