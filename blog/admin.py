from django.contrib import admin
from .models import Post, Comment, Report, CommentReport


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "video_type",
        "live_ended",
        "is_hidden",
    )
    list_filter = ("video_type", "live_ended")

    fields = (
        "author",
        "body",
        "video_url",
        "video_type",
        "live_ended",
        "image",
        "is_hidden",
    )

    actions = ["hide_posts", "unhide_posts"]

    @admin.action(description="選択した投稿を非表示にする")
    def hide_posts(self, request, queryset):
        updated = queryset.update(is_hidden=True)
        self.message_user(request, f"{updated}件の投稿を非表示にしました")

    @admin.action(description="選択した投稿を再表示する")
    def unhide_posts(self, request, queryset):
        updated = queryset.update(is_hidden=False)
        self.message_user(request, f"{updated}件の投稿を再表示しました")


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
        "is_hidden", 
    )

    list_filter = ("posted_date", "is_hidden")
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
        "is_hidden",
    )

    readonly_fields = ("posted_date",)

    actions = ["hide_comments", "unhide_comments"]

    @admin.action(description="選択したコメントを非表示にする")
    def hide_comments(self, request, queryset):
        updated = queryset.update(is_hidden=True)
        self.message_user(request, f"{updated}件のコメントを非表示にしました")

    @admin.action(description="選択したコメントを再表示する")
    def unhide_comments(self, request, queryset):
        updated = queryset.update(is_hidden=False)
        self.message_user(request, f"{updated}件のコメントを再表示しました")

    # ===== 表示用メソッド =====

    def display_author(self, obj):
        return obj.author.username if obj.author else obj.name

    display_author.short_description = "投稿者"

    def display_reply_to(self, obj):
        return obj.reply_to.username if obj.reply_to else "-"

    display_reply_to.short_description = "返信先"


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "post",
        "reported_user",
        "reporter",
        "reason",
        "created_at",
        "report_count",
    )

    list_select_related = ("post", "reporter")

    def reported_user(self, obj):
        return obj.post.author
    reported_user.short_description = "通報されたユーザー"

    def report_count(self, obj):
        return obj.post.reports.count()
    report_count.short_description = "通報件数"


@admin.register(CommentReport)
class CommentReportAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "comment",
        "reported_user",
        "reporter",
        "reason",
        "created_at",
        "report_count",
    )

    list_select_related = ("comment", "reporter")

    def reported_user(self, obj):
        return obj.comment.author
    reported_user.short_description = "通報されたユーザー"

    def report_count(self, obj):
        return obj.comment.reports.count()
    report_count.short_description = "通報件数"