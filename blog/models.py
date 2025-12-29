from django.db import models
from faker import Faker
from django.utils.text import slugify
import unicodedata
from uuid import uuid4
from django.conf import settings

fake = Faker()


class Post(models.Model):
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="blog_posts",
        null=True,
        blank=True,
    )

    # 表示名（ユーザー名 or 識別ID）
    name = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name="表示名"
    )

    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)
    body = models.TextField()
    posted_date = models.DateTimeField(auto_now_add=True)

    image = models.ImageField(upload_to="post_images/", null=True, blank=True)
    video_url = models.URLField(blank=True, null=True)

    def save(self, *args, **kwargs):
        # =========================
        # 表示名の最終確定
        # =========================

        if self.author:
            # ログインユーザー → username
            self.name = self.author.username

        else:
            # 未ログイン → すでに入っている name を尊重
            if not self.name:
                self.name = "未ログインユーザー"

        # =========================
        # slug 自動生成
        # =========================
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

class Comment(models.Model):
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

    def save(self, *args, **kwargs):
        # 表示名が未設定なら強制的に未ログインユーザー
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