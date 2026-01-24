from django.db import models
from faker import Faker
from django.utils.text import slugify
import unicodedata
from uuid import uuid4
from django.conf import settings
from django.urls import reverse

fake = Faker()


class Post(models.Model):
    VIDEO_TYPE_CHOICES = [
            ("normal", "通常動画"),
            ("live", "ライブ配信"),
        ]
    
    @property
    def is_effective_live(self):
        return (
            self.live_ended and
            (
                self.video_type == "live"
                or self.is_live_only_service()
            )
        )

    video_url = models.URLField(blank=True, null=True)
    video_type = models.CharField(
        max_length=10,
        choices=VIDEO_TYPE_CHOICES,
        default="normal",
    )

        # ライブ配信用（任意だが超おすすめ）
    live_ended = models.BooleanField(default=False)

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="blog_posts",
        null=True,
        blank=True,
    )

    name = models.CharField(max_length=50, blank=True, null=True)
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)
    body = models.TextField()
    posted_date = models.DateTimeField(auto_now_add=True)

    image = models.ImageField(upload_to="post_images/", null=True, blank=True)

    def is_live_only_service(self):
        if not self.video_url:
            return False

        live_services = [
            "pococha.com",
            "www.pococha.com",
            "17.live",
            "www.17.live",
            "live.nicovideo.jp",
            "www.live.nicovideo.jp",
            "nico.ms",
        ]

        return any(service in self.video_url for service in live_services)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title) or uuid4().hex[:10]
            slug = base_slug
            counter = 1
            while Post.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug

        super().save(*args, **kwargs)

    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse("blog:post_detail", kwargs={"slug": self.slug})

class Comment(models.Model):
    VIDEO_TYPE_CHOICES = [
            ("normal", "通常動画"),
            ("live", "ライブ配信"),
        ]
    
    video_type = models.CharField(
        max_length=10,
        choices=VIDEO_TYPE_CHOICES,
        default="normal",
    )

    live_ended = models.BooleanField(
        default=False,
        help_text="ライブ配信が終了している場合にチェック"
    )

    def is_live_only_service(self):
        if not self.video_url:
            return False

        live_services = [
            "pococha.com",
            "www.pococha.com",
            "17.live",
            "www.17.live",
            "live.nicovideo.jp",
            "www.live.nicovideo.jp",
            "nico.ms",
        ]

        return any(service in self.video_url for service in live_services)

    post = models.ForeignKey(
        "Post",
        on_delete=models.CASCADE,
        related_name="comments"
    )

    # 表示名（自動で入る）
    name = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name="表示名"
    )

    body = models.TextField()

    posted_date = models.DateTimeField(
        auto_now_add=True
    )

    parent = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="replies"
    )

    # Commentモデル
    reply_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="replied_comments"
    )

    image = models.ImageField(
        upload_to="comment_images/",
        null=True,
        blank=True
    )

    video_url = models.URLField(
        blank=True,
        null=True,
        help_text="動画URL（YouTube / TikTok / Instagram / X / Facebook）"
    )

    def save(self, *args, **kwargs):
        if not self.name:
            self.name = "未ログインユーザー"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.body[:20]

    @property
    def root_parent(self):
        """
        返信ツリーの最上位コメントを返す
        """
        comment = self
        while comment.parent:
            comment = comment.parent
        return comment

    class Meta:
        ordering = ["posted_date"]