from django.contrib import admin
from .models import Page, LikeRecord

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
    list_display = ('user', 'page', 'like_count', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('user__username', 'page__title')
    ordering = ('-updated_at',)