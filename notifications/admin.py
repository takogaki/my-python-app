from django.contrib import admin
from .models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "relation",
        "type",
        "created_at",
    )

    list_filter = ("type",)
    search_fields = ("actor__username", "recipient__username")
    ordering = ("-created_at",)

    # 🔥 人間が理解できる表示にする（完全修正版）
    def relation(self, obj):
        actor = obj.actor if obj.actor else "不明ユーザー"
        recipient = obj.recipient

        if obj.type == "footprint":
            return f"{actor} が {recipient} のプロフィールを閲覧"
        elif obj.type == "like":
            return f"{actor} が {recipient} にいいね"
        elif obj.type == "comment":
            return f"{actor} が {recipient} にコメント"
        elif obj.type == "match":
            return f"{actor} と {recipient} がマッチ"
        else:
            return f"{actor} → {recipient}"

    relation.short_description = "内容"