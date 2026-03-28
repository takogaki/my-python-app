from django.contrib import admin
from django.utils.html import format_html
from django.db.models.deletion import Collector
from django.db import router

from .models import CustomUser, KYCSubmission


# =========================
# 🔥 ユーザー完全削除（関連データごと）
# =========================
@admin.action(description="選択したユーザーと関連データを完全削除")
def delete_users_and_all_related_data(modeladmin, request, queryset):
    for user in queryset:
        using = router.db_for_write(user._meta.model)
        collector = Collector(using=using)
        collector.collect([user])
        collector.delete()


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = (
        "username", "email", "is_supporter",
        "first_name", "last_name", "is_active", "is_staff"
    )
    search_fields = ["username", "email"]
    list_filter = ("is_supporter", "is_active")
    actions = [delete_users_and_all_related_data]


# =========================
# 🔥 KYC承認
# =========================
@admin.action(description="承認する")
def approve_kyc(modeladmin, request, queryset):
    for kyc in queryset:
        kyc.status = "approved"
        kyc.save(update_fields=["status"])

        # 🔥 ユーザー状態も同期
        user = kyc.user
        user.verification_status = "verified"
        user.save(update_fields=["verification_status"])


# =========================
# 🔥 KYC却下
# =========================
@admin.action(description="却下する")
def reject_kyc(modeladmin, request, queryset):
    for kyc in queryset:
        kyc.status = "rejected"
        kyc.save(update_fields=["status"])

        # 🔥 ユーザー状態も同期
        user = kyc.user
        user.verification_status = "rejected"
        user.save(update_fields=["verification_status"])


# =========================
# 🔥 KYC削除（超重要）
# =========================
@admin.action(description="削除（ユーザー状態もリセット）")
def delete_kyc_and_reset_user(modeladmin, request, queryset):
    for kyc in queryset:
        user = kyc.user
        kyc.delete()

        # 🔥 ここが今回のバグの核心
        user.verification_status = "unverified"
        user.save(update_fields=["verification_status"])


# =========================
# 🔥 KYC管理（これ1つだけ！）
# =========================
@admin.register(KYCSubmission)
class KYCSubmissionAdmin(admin.ModelAdmin):
    list_display = (
        "id", "user", "status", "created_at",
        "id_image_preview", "selfie_image_preview"
    )
    list_filter = ("status",)
    search_fields = ("user__username",)
    readonly_fields = (
        "created_at",
        "id_image_preview",
        "selfie_image_preview"
    )

    # 🔥 管理アクション（全部ここに集約）
    actions = [
        approve_kyc,
        reject_kyc,
        delete_kyc_and_reset_user
    ]

    # 🔥 画像プレビュー
    def id_image_preview(self, obj):
        if obj.id_image:
            return format_html('<img src="{}" width="200" />', obj.id_image.url)
        return "-"

    def selfie_image_preview(self, obj):
        if obj.selfie_image:
            return format_html('<img src="{}" width="200" />', obj.selfie_image.url)
        return "-"