from django.contrib.auth.models import AbstractUser
from django.db import models
from datetime import date
import uuid
from django.conf import settings
from django.templatetags.static import static
from blog.models import Post

from diary.models import Page, LikeRecord, GuestLikeRecord
from videos.models import PostVideo, PostVideoLike
from blog.models import Post, PostLike


# =========================
# 👤 ユーザー
# =========================
class CustomUser(AbstractUser):

    HOME_CHOICES = [
        ("feed", "フィード"),
        ("messages", "メッセージ"),
        ("index", "ホーム"),
        ("mypage", "マイページ"),
        ("frontpage", "掲示板"),
        ("roomlist", "ビデオチャット"),
    ]

    # ユーザーが自分で選ぶ
    home_screen = models.CharField(
        max_length=20,
        choices=HOME_CHOICES,
        default="feed"
    )

    # 自動最適化を使うか
    auto_home_screen = models.BooleanField(default=False)

    GENDER_CHOICES = [
        ('M', '男性'),
        ('F', '女性'),
        ('O', 'その他'),
    ]

    birth_date = models.DateField(blank=True, null=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True, null=True)

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

    # 🔥 認証状態（これを基準にする）
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

    verified_at = models.DateTimeField(null=True, blank=True)

    received_likes_count = models.IntegerField(default=0)

    # =========================
    # 🔥 共通プロパティ（最重要）
    # =========================
    @property
    def is_verified(self):
        return self.verification_status == "verified"

    # =========================
    # 年齢
    # =========================
    def get_age(self):
        if not self.birth_date:
            return None
        today = date.today()
        age = today.year - self.birth_date.year
        if (today.month, today.day) < (self.birth_date.month, self.birth_date.day):
            age -= 1
        return age

    # =========================
    # プロフ画像（統一）
    # =========================
    def get_profile_image(self):
        if hasattr(self, "profile") and self.profile.profile_image:
            return self.profile.profile_image.url
        return static("accounts/img/default_avatar.png")

    def __str__(self):
        return self.username
    
# ========================
# 👣 ユーザーログ
# =========================
class UserPageLog(models.Model):
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE
    )

    page_name = models.CharField(max_length=30)

    viewed_at = models.DateTimeField(auto_now_add=True)

# =========================
# 🏷 タグ
# =========================
class TagCategory(models.Model):
    name = models.CharField(max_length=50)
    order = models.IntegerField(default=0)

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(max_length=50)
    category = models.ForeignKey(
        TagCategory,
        on_delete=models.CASCADE,
        related_name="tags"
    )

    def __str__(self):
        return self.name


class Profile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile"
    )

    profile_image = models.ImageField(upload_to="profiles/", blank=True, null=True)
    warning_mail_sent = models.BooleanField(default=False)

    warning_sent_at = models.DateTimeField(
        null=True,
        blank=True
    )

    tags = models.ManyToManyField("Tag", blank=True)

    bio = models.TextField(blank=True)

    drinking = models.CharField(max_length=20, blank=True)
    smoking = models.CharField(max_length=20, blank=True)

    job = models.CharField(max_length=100, blank=True)
    income = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return self.user.username


class ProfileTag(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="profile_tags")
    tag = models.ForeignKey("Tag", on_delete=models.CASCADE)

    LEVEL_CHOICES = [
        (1, "少し"),
        (2, "普通"),
        (3, "かなり"),
    ]

    level = models.IntegerField(choices=LEVEL_CHOICES, default=2)

    class Meta:
        unique_together = ("profile", "tag")


# =========================
# 🔥 KYC
# =========================
class KYCSubmission(models.Model):

    STATUS_CHOICES = [
        ("pending", "確認中"),
        ("approved", "承認"),
        ("rejected", "却下"),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="kyc"
    )

    id_image = models.ImageField(upload_to="kyc/id/")
    selfie_image = models.ImageField(upload_to="kyc/selfie/")

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending", db_index=True)

    rejection_reason = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.status}"


class VerificationLog(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    status = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)


# =========================
# ❤️ LIKE
# =========================
class UserLike(models.Model):
    from_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="given_likes",
        on_delete=models.CASCADE
    )
    to_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="received_likes",
        on_delete=models.CASCADE
    )

    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        unique_together = ("from_user", "to_user")
        indexes = [
            models.Index(fields=["from_user"]),
            models.Index(fields=["to_user"]),
        ]

    def __str__(self):
        return f"{self.from_user} → {self.to_user}"

    def is_match(self):
        return UserLike.objects.filter(
            from_user=self.to_user,
            to_user=self.from_user
        ).exists()


# =========================
# 💕 マッチ
# =========================
class Match(models.Model):
    user1 = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="matches_as_user1")
    user2 = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="matches_as_user2")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user1", "user2")

    def __str__(self):
        return f"{self.user1} ❤️ {self.user2}"

    def get_partner(self, user):
        return self.user2 if self.user1 == user else self.user1


# =========================
# 👣 足跡
# =========================
class Footprint(models.Model):
    from_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="footprints_sent",
        on_delete=models.CASCADE
    )
    to_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="footprints_received",
        on_delete=models.CASCADE
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["to_user"]),
            models.Index(fields=["-created_at"]),
        ]

    def __str__(self):
            return f"{self.from_user} → {self.to_user}"

# =========================
# 💾 保存
# =========================
class SavedPost(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)

    saved_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "post")

    def __str__(self):
        return f"{self.user} - {self.post.id}"
    

# =========================
# 🌟 SPIRIT称号
# =========================
class SpiritTitle(models.Model):

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="spirit_title"
    )

    slot1 = models.CharField(max_length=30, blank=True, default="")
    slot2 = models.CharField(max_length=30, blank=True, default="")
    slot3 = models.CharField(max_length=30, blank=True, default="")
    slot4 = models.CharField(max_length=30, blank=True, default="")
    slot5 = models.CharField(max_length=30, blank=True, default="")

    updated_at = models.DateTimeField(auto_now=True)

    def get_title_parts(self):
        return [
            part
            for part in [
                self.slot1,
                self.slot2,
                self.slot3,
                self.slot4,
                self.slot5,
            ]
            if part
        ]

    def get_title(self):
        return " ".join(self.get_title_parts())

    def __str__(self):
        return f"{self.user.username} - {self.get_title()}"


# =========================
# 🌟 SPIRIT称号パーツ
# =========================
class SpiritTitlePart(models.Model):

    SLOT_CHOICES = [
        (1, "第1枠"),
        (2, "第2枠"),
        (3, "第3枠"),
        (4, "第4枠"),
        (5, "第5枠"),
    ]

    slot = models.PositiveSmallIntegerField(
        choices=SLOT_CHOICES,
        verbose_name="選択枠"
    )

    text = models.CharField(
        max_length=30,
        verbose_name="称号パーツ"
    )

    order = models.PositiveIntegerField(
        default=0,
        verbose_name="表示順"
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name="有効"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["slot", "order", "id"]
        indexes = [
            models.Index(fields=["slot", "is_active"]),
        ]

    def __str__(self):
        return f"{self.get_slot_display()}：{self.text}"