from django.conf import settings
from django.db import models


# =========================
# 🎬 投稿（動画・画像統合）
# =========================
class PostVideo(models.Model):
    MEDIA_TYPE_CHOICES = [
        ("video", "動画"),
        ("image", "画像"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="post_videos"
    )

    media_type = models.CharField(
        max_length=10,
        choices=MEDIA_TYPE_CHOICES
    )

    file = models.FileField(upload_to="videos/")

    caption = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    views_count = models.PositiveIntegerField(default=0)

    # 🔥 追加（超重要）
    likes_count = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["-created_at"]),
            models.Index(fields=["user"]),
        ]

    def __str__(self):
        return f"{self.user} - {self.id}"

    def like_count(self):
        return self.likes_count  # 🔥 DBカラム使う

    def comment_count(self):
        return self.comments.count()


# =========================
# ❤️ いいね（完全版）
# =========================
class PostVideoLike(models.Model):

    # 🔐 ログインユーザー
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="liked_videos"
    )

    # 👤 未ログイン識別子
    guest_id = models.CharField(
        max_length=64,
        null=True,
        blank=True
    )

    post = models.ForeignKey(
        PostVideo,
        on_delete=models.CASCADE,
        related_name="likes"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["user"]),
            models.Index(fields=["guest_id"]),
            models.Index(fields=["post"]),
        ]

        # 🔥 制約（どちらか一方で一意）
        constraints = [
            models.UniqueConstraint(
                fields=["user", "post"],
                name="unique_user_like",
                condition=models.Q(user__isnull=False)
            ),
            models.UniqueConstraint(
                fields=["guest_id", "post"],
                name="unique_guest_like",
                condition=models.Q(guest_id__isnull=False)
            ),
        ]

    def __str__(self):
        return f"{self.user or self.guest_id} ❤️ {self.post.id}"


# =========================
# 💬 コメント
# =========================
class PostVideoComment(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    post = models.ForeignKey(
        PostVideo,
        on_delete=models.CASCADE,
        related_name="comments"
    )

    text = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["post"]),
        ]

    def __str__(self):
        return f"{self.user} - {self.post.id}"


# =========================
# 🔖 保存
# =========================
class PostVideoSave(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="saved_post_videos"
    )

    post = models.ForeignKey(
        PostVideo,
        on_delete=models.CASCADE,
        related_name="saved_by"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "post")

    def __str__(self):
        return f"{self.user} 🔖 {self.post.id}"