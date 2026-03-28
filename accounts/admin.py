from django.contrib import admin
from .models import CustomUser, KYCSubmission
from django.db.models.deletion import Collector
from django.db import router

@admin.action(description="選択したユーザーと関連データを完全削除")
def delete_users_and_all_related_data(modeladmin, request, queryset):
    for user in queryset:
        # DjangoのCollectorを使って関連オブジェクトを削除
        using = router.db_for_write(user._meta.model)  # データベースのルーティングを確認
        collector = Collector(using=using)  # Collectorを初期化
        collector.collect([user])  # 対象のユーザーと関連データを収集
        collector.delete()  # 収集したデータをすべて削除


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ("username", "email", "is_supporter", 'first_name', 'last_name', "is_active", 'is_staff')
    search_fields = ['username', 'email']
    list_filter = ("is_supporter", "is_active")
    actions = [delete_users_and_all_related_data]


@admin.register(KYCSubmission)
class KYCSubmissionAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "status", "created_at")
    list_filter = ("status",)
    search_fields = ("user__username",)
    readonly_fields = ("created_at",)

    # 🔥 画像プレビュー
    def id_image_preview(self, obj):
        if obj.id_image:
            return f'<img src="{obj.id_image.url}" width="200" />'
        return "-"
    id_image_preview.allow_tags = True

    def selfie_image_preview(self, obj):
        if obj.selfie_image:
            return f'<img src="{obj.selfie_image.url}" width="200" />'
        return "-"
    selfie_image_preview.allow_tags = True


@admin.action(description="承認する")
def approve_kyc(modeladmin, request, queryset):
    for kyc in queryset:
        kyc.status = "approved"
        kyc.save()

        user = kyc.user
        user.verification_status = "verified"
        user.save(update_fields=["verification_status"])

@admin.register(KYCSubmission)
class KYCSubmissionAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "status", "created_at")
    actions = [approve_kyc]