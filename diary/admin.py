from django.contrib import admin
from .models import Page, LikeRecord, SiteNotice, SiteNoticeRead

@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    readonly_fields = ["id", "created_at", "updated_at"]
    list_display    = ("title", "author", "is_public", "created_at")  # 表示項目にis_publicを追加
    list_filter     = ("is_public", "author")  # 公開状態でフィルタリング可能にする
    search_fields   = ("title", "content", "author__username")  # 検索対象にauthorを追加

    # フォームにis_publicを追加して、管理者が編集できるようにする
    fields = ("title", "body", "page_date", "picture", "is_public")

@admin.register(LikeRecord)
class LikeRecordAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "page",
        "like_count",
        "created_at",
        "updated_at",
    )

    list_filter = (
        "created_at",
        "updated_at",
        "page",
    )

    search_fields = (
        "user__username",
        "page__title",
    )

    autocomplete_fields = ("user", "page")

    ordering = ("-updated_at",)



@admin.register(SiteNotice)
class SiteNoticeAdmin(admin.ModelAdmin):

    list_display = (
        "title",
        "published_at",
        "is_active",
    )

    list_filter = (
        "is_active",
        "published_at",
    )

    search_fields = (
        "title",
        "message",
    )

    ordering = (
        "-published_at",
    )


@admin.register(SiteNoticeRead)
class SiteNoticeReadAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "notice",
        "read_at",
    )

    list_filter = (
        "read_at",
    )

    search_fields = (
        "user__username",
        "notice__title",
    )

    autocomplete_fields = (
        "user",
        "notice",
    )

    ordering = (
        "-read_at",
    )