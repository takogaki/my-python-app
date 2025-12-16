from django.db import models
from faker import Faker
from django.utils.text import slugify
import unicodedata
from uuid import uuid4

fake = Faker()


class Post(models.Model):
    name        = models.CharField(max_length=255, blank=True, null=True)
    title       = models.CharField(max_length=255)
    slug        = models.SlugField(unique=True, blank=True)
    body        = models.TextField(verbose_name="本文")
    posted_date = models.DateTimeField(auto_now_add=True, verbose_name="作成日時")

    image = models.ImageField(
        upload_to="post_images/",
        null=True,
        blank=True
    )
    video = models.FileField(
        upload_to="post_videos/",
        null=True,
        blank=True
    )

    posted_date = models.DateTimeField(auto_now_add=True)

    parent = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="replies"
    )
    reply_to = models.CharField(max_length=50, null=True, blank=True)

    def save(self, *args, **kwargs):
        # ランダムな名前
        if not self.name:
            self.name = fake.name()

        # slug 自動生成
        if not self.slug:
            normalized_title = unicodedata.normalize('NFKD', self.title)
            base_slug = slugify(normalized_title)

            # 日本語タイトルで空になる場合の保険
            if not base_slug:
                base_slug = uuid4().hex[:10]

            self.slug = base_slug

            # 一意性の確保
            counter = 1
            while Post.objects.filter(slug=self.slug).exists():
                self.slug = f"{base_slug}-{counter}"
                counter += 1

        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    name = models.CharField(max_length=50, null=True)
    body = models.TextField()
    posted_date = models.DateTimeField(auto_now_add=True)
    parent = models.ForeignKey(
        'self', null=True, blank=True, on_delete=models.CASCADE, related_name='replies'
    )

# 🔽 追加
    image = models.ImageField(
        upload_to="comment_images/",
        null=True,
        blank=True
    )
    video = models.FileField(
        upload_to="comment_videos/",
        null=True,
        blank=True
    )

    posted_date = models.DateTimeField(auto_now_add=True)

    parent = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="replies"
    )
    reply_to = models.CharField(max_length=50, null=True, blank=True)
    def __str__(self):
        return f"{self.name} >>> {self.reply_to}: {self.body[:20]}"

    @property
    def root_parent(self):
        """必ず一番上の親コメントを返す"""
        comment = self
        while comment.parent:
            comment = comment.parent
        return comment

class Meta:
        ordering = ['posted_date']  # ← ★ここを追加（返信は古い順）