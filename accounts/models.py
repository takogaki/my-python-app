# from django.contrib.auth.models import AbstractUser
# from django.db import models
# from datetime import date

# class CustomUser(AbstractUser):
#     GENDER_CHOICES = [
#         ('M', '男性'),
#         ('F', '女性'),
#         ('O', 'その他'),
#     ]
    
#     # ユーザID（ログイン時に使用）
#     username = models.CharField(
#         max_length=50, 
#         unique=True, 
#         verbose_name="ユーザID (ログインの時使います。他のユーザに見える部分です。)"
#     )
    
#     # パスワード（ログイン時に使用）
#     password = models.CharField(
#         max_length=100, 
#         verbose_name="パスワード (ログインの時使います。)"
#     )

#     # 名前
#     name = models.CharField(max_length=100, verbose_name="名前")
    
#     # 生年月日
#     birth_date = models.DateField(blank=True, null=True, verbose_name="生年月日")
    
#     # 性別
#     gender = models.CharField(
#         max_length=10, 
#         choices=GENDER_CHOICES, 
#         verbose_name="任意)性別",
#         blank=True,
#         null=True
#     )

#     # 住所
#     address = models.CharField(max_length=255, blank=True, null=True, verbose_name="任意)住所")
    
#     # 緊急連絡先電話番号
#     emergency_contact_phone = models.CharField(max_length=15, verbose_name="連絡先電話番号")
    
#     # メールアドレス
#     email = models.EmailField(unique=True, verbose_name="メールアドレス")

#     # 年齢計算メソッド
#     def get_age(self):
#         """現在の年齢を計算して返す"""
#         if self.birth_date:
#             today = date.today()
#             age = today.year - self.birth_date.year
#             if (today.month, today.day) < (self.birth_date.month, self.birth_date.day):
#                 age -= 1
#             return age
#         return None

#     # 性別を日本語で表示するメソッド
#     def get_gender_display(self):
#         """性別を日本語で返す"""
#         return dict(self.GENDER_CHOICES).get(self.gender, "未設定")

#     # Djangoの設定に必要なフィールド指定
#     USERNAME_FIELD = 'username'
#     REQUIRED_FIELDS = ['name', 'birth_date', 'gender', 'address', 'emergency_contact_phone', 'email']

# accounts/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models
from datetime import date

class CustomUser(AbstractUser):
    GENDER_CHOICES = [
        ('M', '男性'),
        ('F', '女性'),
        ('O', 'その他'),
    ]

    # 既存のまま
    birth_date = models.DateField(
        blank=True,
        null=True,
        verbose_name="生年月日"
    )

    gender = models.CharField(
        max_length=1,
        choices=GENDER_CHOICES,
        blank=True,
        null=True,
        verbose_name="性別"
    )

    # 🔽 追加（安全）
    profile_image = models.ImageField(
        upload_to="profile_images/",
        blank=True,
        null=True,
        verbose_name="プロフィール画像"
    )

    # 🔽 メール認証用（既存のDjango仕様）
    is_active = models.BooleanField(default=False)

    def get_age(self):
        if not self.birth_date:
            return None
        today = date.today()
        age = today.year - self.birth_date.year
        if (today.month, today.day) < (self.birth_date.month, self.birth_date.day):
            age -= 1
        return age