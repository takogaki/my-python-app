# accounts/signals.py
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Profile, KYCSubmission

User = get_user_model()

# =========================
# プロフィール自動作成
# =========================
@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


# =========================
# 🔥 KYC → User同期（最重要）
# =========================
@receiver(post_save, sender=KYCSubmission)
def sync_user_verification_status(sender, instance, **kwargs):
    user = instance.user

    if instance.status == "approved":
        user.verification_status = "verified"
    elif instance.status == "pending":
        user.verification_status = "pending"
    elif instance.status == "rejected":
        user.verification_status = "rejected"
    else:
        user.verification_status = "unverified"

    user.save(update_fields=["verification_status"])


# =========================
# 🔥 削除時リセット
# =========================
@receiver(post_delete, sender=KYCSubmission)
def reset_user_verification_on_delete(sender, instance, **kwargs):
    user = instance.user
    user.verification_status = "unverified"
    user.save(update_fields=["verification_status"])