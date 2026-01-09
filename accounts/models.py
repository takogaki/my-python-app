# accounts/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models
from datetime import date
import uuid
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model

class CustomUser(AbstractUser):
    GENDER_CHOICES = [
        ('M', '男性'),
        ('F', '女性'),
        ('O', 'その他'),
    ]

    # 既存のまま
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

    # 🔽 追加（安全）
    profile_image = models.ImageField(
        upload_to="profile_images/",
        blank=True,
        null=True,
        verbose_name="プロフィール画像"
    )

    # 🔽 メール認証用（既存のDjango仕様）
    is_active = models.BooleanField(default=False)

    def get_age(self):
        if not self.birth_date:
            return None
        today = date.today()
        age = today.year - self.birth_date.year
        if (today.month, today.day) < (self.birth_date.month, self.birth_date.day):
            age -= 1
        return age
    

    activation_token = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        null=True,
        blank=True
    )

    is_supporter = models.BooleanField(default=False)


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