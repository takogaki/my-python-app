from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Message(models.Model):
    sender       = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="sent_messages"
    )
    recipient    = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="received_messages"
    )
    content      = models.TextField()

    # 時刻は sent_at に統一（既存DBと一致）
    sent_at      = models.DateTimeField(auto_now_add=True)

    # フラグ類
    is_read      = models.BooleanField(default=False)
    is_important = models.BooleanField(default=False)

    class Meta:
        ordering = ["-sent_at"]

    def __str__(self):
        return f"From {self.sender.username} to {self.recipient.username} at {self.sent_at}"