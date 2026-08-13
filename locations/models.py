from django.conf import settings
from django.db import models


# ==================================================
# 📍 ユーザー位置情報
# ==================================================

class UserLocation(models.Model):

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="location",
    )

    latitude = models.FloatField()

    longitude = models.FloatField()

    is_active = models.BooleanField(
        default=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        indexes = [
            models.Index(
                fields=["latitude", "longitude"]
            ),
        ]

    def __str__(self):
        return (
            f"{self.user.username} "
            f"({self.latitude}, {self.longitude})"
        )