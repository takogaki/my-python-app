from django.db import models
from django.conf import settings


class Notification(models.Model):
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications"
    )

    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="acted_notifications"
    )

    verb = models.CharField(max_length=255)

    # ⭐ 追加：どの投稿の通知か
    post = models.ForeignKey(
        "blog.Post",              # ← あなたのPostモデルに合わせる
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="notifications"
    )

    target_url = models.CharField(
        max_length=500,
        blank=True
    )

    is_read = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.recipient} - {self.verb}"