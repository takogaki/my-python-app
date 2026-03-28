from django.contrib import admin
from django.utils.html import format_html
from .models import CustomUser, KYCSubmission
from django.db.models.deletion import Collector
from django.db import router


@admin.action(description="選択したユーザーと関連データを完全削除")
def delete_users_and_all_related_data(modeladmin, request, queryset):
    for user in queryset:
        using = router.db_for_write(user._meta.model)
        collector = Collector(using=using)
        collector.collect([user])
        collector.delete()


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ("username", "email", "is_supporter", "first_name", "last_name", "is_active", "is_staff")
    search_fields = ["username", "email"]
    list_filter = ("is_supporter", "is_active")
    actions = [delete_users_and_all_related_data]


# =========================
# 🔥 KYC承認アクション
# =========================
@admin.action(description="承認する")
def approve_kyc(modeladmin, request, queryset):
    for kyc in queryset:
        kyc.status = "approved"
        kyc.save()

        user = kyc.user
        user.verification_status = "verified"
        user.save(update_fields=["verification_status"])


# =========================
# 🔥 KYC管理（これ1つだけ！）
# =========================
@admin.register(KYCSubmission)
class KYCSubmissionAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "status", "created_at", "id_image_preview", "selfie_image_preview")
    list_filter = ("status",)
    search_fields = ("user__username",)
    readonly_fields = ("created_at", "id_image_preview", "selfie_image_preview")
    actions = [approve_kyc]

    def id_image_preview(self, obj):
        if obj.id_image:
            return format_html('<img src="{}" width="200" />', obj.id_image.url)
        return "-"

    def selfie_image_preview(self, obj):
        if obj.selfie_image:
            return format_html('<img src="{}" width="200" />', obj.selfie_image.url)
        return "-"