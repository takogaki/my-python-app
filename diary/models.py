from django.db import models
from pathlib import Path
from django.conf import settings  # settings.AUTH_USER_MODELを使用するため
from django.utils import timezone
from cloudinary.models import CloudinaryField
import uuid, cloudinary.uploader



class Page(models.Model):

    class Meta:
        ordering = ["-page_date"]

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name="ID"
    )

    title = models.CharField(max_length=100)
    body = models.TextField(max_length=2000)

    page_date = models.DateField(default=timezone.now)

    # Cloudinary画像
    picture = CloudinaryField(
        "image",
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    is_public = models.BooleanField(default=False)

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="pages"
    )

    likes = models.PositiveIntegerField(default=0)

    liked_users = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="liked_pages",
        blank=True
    )

    def unique_likes_count(self):
        return self.liked_users.count()

    def __str__(self):
        return self.title

    # 投稿削除時にCloudinary画像削除
    picture = CloudinaryField("image", blank=True, null=True)

    def delete(self, *args, **kwargs):

        if self.picture:
            cloudinary.uploader.destroy(self.picture.public_id)

        super().delete(*args, **kwargs)

    @classmethod
    def get_public_pages_by_user(cls, user):
        return cls.objects.filter(author=user, is_public=True)
    

class LikeRecord(models.Model):
    """
    誰がどの日記に何回いいねしたかを記録するモデル
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="like_records",
        verbose_name="ユーザー"
    )
    page = models.ForeignKey(
        Page,
        on_delete=models.CASCADE,
        related_name="like_records",
        verbose_name="日記"
    )
    like_count = models.PositiveIntegerField(
        default=0,
        verbose_name="いいね回数"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="作成日時"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="更新日時"
    )

    class Meta:
        unique_together = ('user', 'page')  # ユーザーと日記の組み合わせをユニークにする

    def __str__(self):
        """
        モデルの文字列表現
        """
        return f"{self.user.username} - {self.page.title} ({self.like_count}回)"