from django.contrib.auth.models import AbstractUser
from django.db import models
from datetime import date
import uuid
from django.conf import settings
from blog.models import Post


class CustomUser(AbstractUser):
    GENDER_CHOICES = [
        ('M', '男性'),
        ('F', '女性'),
        ('O', 'その他'),
    ]

    birth_date = models.DateField(
        blank=True,
        null=True,
        verbose_name="生年月日"
    )

    gender = models.CharField(
        max_length=1,
        choices=GENDER_CHOICES,
        blank=True,
        null=True,
        verbose_name="性別"
    )

    profile_image = models.ImageField(
        upload_to="profiles/",
        blank=True,
        null=True,
    )

    is_active = models.BooleanField(default=False)

    activation_token = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        null=True,
        blank=True
    )

    is_supporter = models.BooleanField(default=False)

    agreed_terms_at = models.DateTimeField(null=True, blank=True)
    terms_version = models.CharField(max_length=10, default="1.0")

    # =========================
    # 🔥 年齢認証（完全版）
    # =========================
    verification_status = models.CharField(
        max_length=20,
        choices=[
            ("unverified", "未確認"),
            ("pending", "確認中"),
            ("verified", "確認済み"),
            ("failed", "失敗"),
        ],
        default="unverified",
        db_index=True
    )

    verification_attempts = models.IntegerField(default=0)

    verified_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="認証日時"
    )
    # =========================

    def get_age(self):
        if not self.birth_date:
            return None
        today = date.today()
        age = today.year - self.birth_date.year
        if (today.month, today.day) < (self.birth_date.month, self.birth_date.day):
            age -= 1
        return age

    def get_profile_image(self):
        if self.profile_image:
            return self.profile_image.url
        if hasattr(self, "profile") and self.profile.profile_image:
            return self.profile.profile_image.url
        return "/static/accounts/img/default_avatar.png"

    def __str__(self):
        return self.username


# =========================
# 🔥 KYC申請（最重要）
# =========================
class KYCSubmission(models.Model):
    STATUS_CHOICES = [
        ("pending", "確認中"),
        ("approved", "承認"),
        ("rejected", "却下"),
    ]

    # 🔥 1ユーザー1件（超重要）
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="kyc"
    )

    id_image = models.ImageField(upload_to="kyc/id/")
    selfie_image = models.ImageField(upload_to="kyc/selfie/")

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending",
        db_index=True
    )

    # 任意：却下理由
    rejection_reason = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.status}"


# =========================
# 🔥 認証ログ
# =========================
class VerificationLog(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    status = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.status}"


class Profile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile"
    )

    profile_image = models.ImageField(
        upload_to="profiles/",
        blank=True,
        null=True
    )

    def __str__(self):
        return self.user.username


class SavedPost(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE
    )

    saved_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "post")

    def __str__(self):
        return f"{self.user.username} - {self.post.id}"


class UserLike(models.Model):
    from_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="likes_sent",
        on_delete=models.CASCADE
    )

    to_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="likes_received",
        on_delete=models.CASCADE
    )

    created_at = models.DateTimeField(auto_now_add=True)

    is_read = models.BooleanField(default=False)

    class Meta:
        unique_together = ("from_user", "to_user")

    def __str__(self):
        return f"{self.from_user.username} → {self.to_user.username}"

    def is_match(self):
        return UserLike.objects.filter(
            from_user=self.to_user,
            to_user=self.from_user
        ).exists()

    def save(self, *args, **kwargs):
        if self.from_user == self.to_user:
            return
        super().save(*args, **kwargs)


class Match(models.Model):
    user1 = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="matches_as_user1"
    )
    user2 = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="matches_as_user2"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user1", "user2")

    def __str__(self):
        return f"{self.user1} ❤️ {self.user2}"
    
    
# =========================
# 🔥 足跡（最重要）
# =========================
class Footprint(models.Model):
    from_user = models.ForeignKey(
        CustomUser,
        related_name="footprints_sent",
        on_delete=models.CASCADE
    )
    to_user = models.ForeignKey(
        CustomUser,
        related_name="footprints_received",
        on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(auto_now_add=True)