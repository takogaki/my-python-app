from django.db import models
from django.conf import settings


class Post(models.Model):
    MEDIA_TYPES = (
        ("video", "Video"),
        ("image", "Image"),
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    media_type = models.CharField(max_length=10, choices=MEDIA_TYPES)

    file = models.FileField(upload_to="posts/")
    caption = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)


class Engagement(models.Model):
    ENGAGEMENT_TYPES = (
        ("like", "Like"),
        ("comment", "Comment"),
        ("view", "View"),
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    post = models.ForeignKey(Post, null=True, blank=True, on_delete=models.CASCADE)

    type = models.CharField(max_length=10, choices=ENGAGEMENT_TYPES)

    text = models.TextField(blank=True, null=True)
    watch_time = models.FloatField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)