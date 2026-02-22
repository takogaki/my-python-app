# accounts/models.py

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
        upload_to="profile_images/",
        blank=True,
        null=True,
        verbose_name="プロフィール画像"
    )

    is_active = models.BooleanField(default=False)

    activation_token = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        null=True,
        blank=True
    )

    is_supporter = models.BooleanField(default=False)

    def get_age(self):
        if not self.birth_date:
            return None
        today = date.today()
        age = today.year - self.birth_date.year
        if (today.month, today.day) < (self.birth_date.month, self.birth_date.day):
            age -= 1
        return age

    def get_profile_image(self):
        """
        テンプレート用安全取得
        既存構造を壊さない
        """
        if self.profile_image:
            return self.profile_image.url
        if hasattr(self, "profile") and self.profile.profile_image:
            return self.profile.profile_image.url
        return "/static/accounts/img/default_avatar.png"

    def __str__(self):
        return self.username


class Profile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile"
    )

    profile_image = models.ImageField(
        upload_to="profile_images/",
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

    class Meta:
        unique_together = ("from_user", "to_user")

    def __str__(self):
        return f"{self.from_user.username} → {self.to_user.username}"