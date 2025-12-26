from django.db import models
from faker import Faker
from django.utils.text import slugify
import unicodedata
from uuid import uuid4

fake = Faker()


class Post(models.Model):
    name = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="投稿者名"
    )

    title = models.CharField(
        max_length=255,
        verbose_name="タイトル"
    )

    slug = models.SlugField(
        unique=True,
        blank=True,
        db_index=True,  # 🔒 本番での検索最適化
    )

    body = models.TextField(
        verbose_name="本文"
    )

    posted_date = models.DateTimeField(
        auto_now_add=True
    )

    image = models.ImageField(
        upload_to="post_images/",
        null=True,
        blank=True
    )

    # ★ すべての動画SNS用（安全なURLは forms.py 側で厳格に検証）
    video_url = models.URLField(
        blank=True,
        null=True,
        help_text="YouTube / TikTok / Instagram / X / Facebook の動画URL"
    )

    def save(self, *args, **kwargs):
        # 投稿者名が無ければ自動生成（既存挙動そのまま）
        if not self.name:
            self.name = fake.name()

        # slug 自動生成（日本語・空文字完全対応）
        if not self.slug:
            normalized_title = unicodedata.normalize("NFKD", self.title)
            base_slug = slugify(normalized_title)

            if not base_slug:
                base_slug = uuid4().hex[:10]

            slug = base_slug
            counter = 1
            while Post.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1

            self.slug = slug

        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name="comments"
    )

    name = models.CharField(
        max_length=50,
        blank=True,
        null=True
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

    reply_to = models.CharField(
        max_length=50,
        null=True,
        blank=True
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