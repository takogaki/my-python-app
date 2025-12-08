# from django.db import models
# from faker import Faker
# from django.utils.text import slugify
# import unicodedata

# fake = Faker()  # Fakerのインスタンスを作成

# class Post(models.Model):
#     name        = models.CharField(max_length=255, blank=True, null=True)
#     title       = models.CharField(max_length=255)
#     slug        = models.SlugField(unique=True, blank=True)
#     body        = models.TextField(verbose_name="本文")
#     posted_date = models.DateTimeField(auto_now_add=True, verbose_name="作成日時")

#     def save(self, *args, **kwargs):
#         # Fakerでランダムネーム
#         if not self.name:
#             self.name = fake.name()

#         # slug生成
#         if not self.slug:
#             # ✨ unicodedata.normalize を使用
#             normalized_title = unicodedata.normalize('NFKD', self.title)
#             original_slug = slugify(normalized_title)

#             self.slug = original_slug

#             # ユニークなslugが必要な場合
#             counter = 1
#             while Post.objects.filter(slug=self.slug).exists():
#                 self.slug = f"{original_slug}-{counter}"
#                 counter += 1

#         super().save(*args, **kwargs)

#     def __str__(self):
#         return self.title


# class Comment(models.Model):
#     post = models.ForeignKey('Post', on_delete=models.CASCADE, related_name='comments')
#     name = models.CharField(max_length=50, null=True)
#     body = models.TextField()
#     posted_date = models.DateTimeField(auto_now_add=True)
#     parent = models.ForeignKey(
#         'self', null=True, blank=True, on_delete=models.CASCADE, related_name='replies'
#     )
#     reply_to = models.CharField(max_length=50, null=True, blank=True)

#     def __str__(self):
#         return f"{self.name} >>> {self.reply_to}: {self.body[:20]}"







# from django.db import models
# from faker import Faker
# from django.utils.text import slugify
# import unicodedata

# fake = Faker()  # Fakerのインスタンスを作成

# #blog
# class Post(models.Model):
#     name        = models.CharField(max_length=255, blank=True, null=True)  # 投稿者の名前（ランダム）
#     title       = models.CharField(max_length=255)
#     slug        = models.SlugField(unique=True, blank=True)
#     body        = models.TextField(verbose_name="本文")
#     posted_date = models.DateTimeField(auto_now_add=True, verbose_name="作成日時")

#     def save(self, *args, **kwargs):
#         if not self.name:
#             self.name = fake.name()  # 名前がなければFakerで生成

#         if not self.slug:
#             # 日本語をローマ字に変換した後にslugを生成
#             original_slug = slugify(unicodedata(self.title))
#             self.slug = original_slug
#             # ユニークなslugを作成
#             counter = 1
#             while Post.objects.filter(slug=self.slug).exists():
#                 self.slug = f"{original_slug}-{counter}"
#                 counter += 1

#         super().save(*args, **kwargs)

#     def __str__(self):
#         return self.title


#     def __str__(self):
#         return self.title

# from django.db import models

# class Comment(models.Model):
#     post = models.ForeignKey('Post', on_delete=models.CASCADE, related_name='comments')
#     name = models.CharField(max_length=50, null=True)  # コメントしたユーザーの名前
#     body = models.TextField()
#     posted_date = models.DateTimeField(auto_now_add=True)
#     parent = models.ForeignKey(
#         'self', null=True, blank=True, on_delete=models.CASCADE, related_name='replies'
#     )
#     reply_to = models.CharField(max_length=50, null=True, blank=True)  # 宛名を保存

#     def __str__(self):
#         return f"{self.name} >>> {self.reply_to}: {self.body[:20]}"
    



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

    def save(self, *args, **kwargs):
        # ランダムな名前
        if not self.name:
            self.name = fake.name()

        # slug 自動生成
        if not self.slug:
            normalized_title = unicodedata.normalize('NFKD', self.title)
            base_slug = slugify(normalized_title)

            # ▼ 日本語タイトルのとき slugify が空になる対策
            if not base_slug:
                base_slug = uuid4().hex[:10]  # ランダム英数字

            self.slug = base_slug

            # ▼ 一意性の確保
            counter = 1
            while Post.objects.filter(slug=self.slug).exists():
                self.slug = f"{base_slug}-{counter}"
                counter += 1

        super().save(*args, **kwargs)

    def __str__(self):
        return self.title



