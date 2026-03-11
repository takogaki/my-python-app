from django.db import models
from pathlib import Path
from django.conf import settings  # settings.AUTH_USER_MODELを使用するため
from django.utils import timezone
import uuid


class Page(models.Model):
    class Meta:
        ordering = ["-page_date"]  # 日付の降順で表示

    """
    日記ページを表すモデル
    """
    # 基本情報
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name="ID"
    )
    title = models.CharField(
        max_length=100,
        verbose_name="タイトル"
    )
    body = models.TextField(
        max_length=2000,
        verbose_name="本文"
    )
    page_date = models.DateField(
        default=timezone.now,
        verbose_name="日付"
    )
    picture = models.ImageField(
        upload_to="diary/picture/",
        blank=True,
        null=True,
        verbose_name="写真"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="作成日時"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="更新日時"
    )
    is_public = models.BooleanField(
        default=False,
        verbose_name="☑️で公開"
    )  # 公開設定

    # 作成者情報
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="pages",
        verbose_name="作成者"
    )

    # いいね関連
    likes = models.PositiveIntegerField(
        default=0,
        verbose_name="いいね数"
    )
    liked_users = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="liked_pages",
        blank=True,
        verbose_name="いいねしたユーザー"
    )

    def unique_likes_count(self):
        """
        👍を押したユニークユーザー数
        """
        return self.liked_users.count()

    def __str__(self):
        """
        モデルの文字列表現
        """
        return self.title

    def delete(self, *args, **kwargs):
        """
        インスタンス削除時に関連する画像ファイルを削除する
        """
        picture = self.picture
        super().delete(*args, **kwargs)
        if picture:
            Path(picture.path).unlink(missing_ok=True)

    @classmethod
    def get_public_pages_by_user(cls, user):
        """
        指定されたユーザーの公開日記を取得する
        """
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