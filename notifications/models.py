from django.db import models
from django.conf import settings

class Notification(models.Model):

    TYPE_CHOICES = [
        ("like", "いいね"),
        ("footprint", "足跡"),
        ("match", "マッチ"),
        ("comment", "コメント"),
        ("message", "メッセージ"),
        ("tag_match", "タグ一致"),
        ("system", "システム"),
    ]

    type = models.CharField(
        max_length=50,
        choices=TYPE_CHOICES,
        default="system"
    )

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

    post = models.ForeignKey(
        "blog.Post",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="notifications"
    )

    is_read = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.actor:
            return f"{self.actor} が {self.recipient} に {self.verb}"
        return f"{self.recipient} に {self.verb}"