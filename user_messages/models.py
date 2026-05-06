from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sent_messages")
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name="received_messages")
    content = models.TextField()

    sent_at = models.DateTimeField(auto_now_add=True)

    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)

    is_important = models.BooleanField(default=False)

    class Meta:
        ordering = ["sent_at"]
        indexes = [
            models.Index(fields=["sender", "recipient"]),
            models.Index(fields=["recipient", "is_read"]),
            models.Index(fields=["sent_at"]),
        ]

    def __str__(self):
        return f"{self.sender} → {self.recipient} ({self.sent_at})"