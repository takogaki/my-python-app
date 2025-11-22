from django.db import models
from faker import Faker
from django.utils.text import slugify
from unicodedata
import unicodedata

fake = Faker()  # Fakerのインスタンスを作成

#blog
class Post(models.Model):
    name        = models.CharField(max_length=255, blank=True, null=True)  # 投稿者の名前（ランダム）
    title       = models.CharField(max_length=255)
    slug        = models.SlugField(unique=True, blank=True)
    body        = models.TextField(verbose_name="本文")
    posted_date = models.DateTimeField(auto_now_add=True, verbose_name="作成日時")

    def save(self, *args, **kwargs):
        if not self.name:
            self.name = fake.name()  # 名前がなければFakerで生成

        if not self.slug:
            # 日本語をローマ字に変換した後にslugを生成
            original_slug = slugify(unicodedata(self.title))
            self.slug = original_slug
            # ユニークなslugを作成
            counter = 1
            while Post.objects.filter(slug=self.slug).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1

        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


    def __str__(self):
        return self.title

from django.db import models

class Comment(models.Model):
    post = models.ForeignKey('Post', on_delete=models.CASCADE, related_name='comments')
    name = models.CharField(max_length=50, null=True)  # コメントしたユーザーの名前
    body = models.TextField()
    posted_date = models.DateTimeField(auto_now_add=True)
    parent = models.ForeignKey(
        'self', null=True, blank=True, on_delete=models.CASCADE, related_name='replies'
    )
    reply_to = models.CharField(max_length=50, null=True, blank=True)  # 宛名を保存

    def __str__(self):
        return f"{self.name} >>> {self.reply_to}: {self.body[:20]}"