from django import forms
from django.core.exceptions import ValidationError
from urllib.parse import urlparse
from faker import Faker
from .validators import validate_video_url

from .models import Post, Comment

fake = Faker()

# =======================
# 許可する動画ドメイン（本番用）
# =======================
ALLOWED_VIDEO_DOMAINS = {
    "youtube.com",
    "www.youtube.com",
    "youtu.be",
    "tiktok.com",
    "www.tiktok.com",
    "instagram.com",
    "www.instagram.com",
    "twitter.com",
    "www.twitter.com",
    "x.com",
    "www.x.com",
    "facebook.com",
    "www.facebook.com",
}

# =======================
# 共通URLバリデーション関数
# =======================
def validate_video_url(url: str | None):
    """
    悪意あるURLを本番環境で確実に弾く
    """
    if not url:
        return None

    parsed = urlparse(url)

    # スキーム制限（javascript:, data: 等を完全拒否）
    if parsed.scheme not in ("http", "https"):
        raise ValidationError("不正なURL形式です。")

    # ドメイン取得（ポート番号除去）
    domain = parsed.netloc.lower().split(":")[0]

    if domain not in ALLOWED_VIDEO_DOMAINS:
        raise ValidationError("この動画サービスは利用できません。")

    return url


# =======================
# Post の投稿フォーム
# =======================
class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ["title", "body", "image", "video_url"]
        widgets = {
            "title": forms.TextInput(attrs={"placeholder": "タイトル"}),
            "body": forms.Textarea(attrs={
                "placeholder": "本文を入力してください",
                "rows": 6,
            }),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

    def clean_video_url(self):
        video_url = self.cleaned_data.get("video_url")

        if not video_url:
            return None

        if not self.user or not self.user.is_authenticated:
            raise ValidationError("動画の投稿にはログインが必要です。")

        return validate_video_url(video_url)
    

# =======================
# コメントフォーム
# =======================
class CommentForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = ["body", "image", "video_url"]
        widgets = {
            "body": forms.Textarea(attrs={
                "placeholder": "コメントを書く",
                "rows": 3,
            }),
        }

    def __init__(self, *args, **kwargs):
        self.parent = kwargs.pop("parent", None)
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        if self.parent:
            parent_name = self.parent.name or "未ログインユーザー"
            self.fields["body"].widget.attrs["placeholder"] = (
                f"{parent_name} さんに返信する"
            )

    def clean_video_url(self):
        video_url = self.cleaned_data.get("video_url")

        if not video_url:
            return None

        if not self.user or not self.user.is_authenticated:
            raise ValidationError("動画の投稿にはログインが必要です。")

        return validate_video_url(video_url)