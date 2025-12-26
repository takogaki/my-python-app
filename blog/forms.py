from django import forms
from django.core.exceptions import ValidationError
from urllib.parse import urlparse
from faker import Faker

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
    name = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                "placeholder": "匿名可",
            }
        ),
        label="名前",
    )

    class Meta:
        model = Post
        fields = ["name", "title", "body", "image", "video_url"]
        widgets = {
            "title": forms.TextInput(attrs={
                "placeholder": "タイトル",
            }),
            "body": forms.Textarea(attrs={
                "placeholder": "本文を入力してください",
                "rows": 6,
            }),
        }

    def clean_name(self):
        """
        名前が未入力の場合は None を返す
        （Model.save() 側で faker による自動補完が動く）
        """
        name = self.cleaned_data.get("name")
        return name or None

    def clean_video_url(self):
        """
        本番環境用：安全な動画URLのみ許可
        """
        return validate_video_url(self.cleaned_data.get("video_url"))


# =======================
# コメントフォーム
# =======================
class CommentForm(forms.ModelForm):
    name = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                "placeholder": "匿名可",
            }
        ),
        label="名前",
    )

    class Meta:
        model = Comment
        fields = ["name", "body", "image", "video_url"]
        widgets = {
            "body": forms.Textarea(attrs={
                "placeholder": "コメントを書く",
                "rows": 3,
            }),
        }

    def __init__(self, *args, **kwargs):
        self.parent = kwargs.pop("parent", None)
        super().__init__(*args, **kwargs)

        # 返信時のプレースホルダー変更（既存挙動維持）
        if self.parent:
            parent_name = self.parent.name or "匿名"
            self.fields["body"].widget.attrs["placeholder"] = (
                f"{parent_name} さんに返信する"
            )

    def clean_name(self):
        """
        未入力なら None（Model 側で処理）
        """
        name = self.cleaned_data.get("name")
        return name or None

    def clean_video_url(self):
        """
        本番環境用：安全な動画URLのみ許可
        """
        return validate_video_url(self.cleaned_data.get("video_url"))