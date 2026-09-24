from django import forms
from django.core.exceptions import ValidationError
from urllib.parse import urlparse
from .validators import validate_video_url
from django.core.validators import FileExtensionValidator

from .models import Post, Comment

# =========================
# 複数画像アップロード用
# =========================

class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        if not data:
            return []

        if isinstance(data, (list, tuple)):
            return [
                forms.FileField.clean(self, item, initial)
                for item in data
            ]

        return [
            forms.FileField.clean(self, data, initial)
        ]

# =======================
# 許可する動画ドメイン（本番用）
# =======================
ALLOWED_VIDEO_DOMAINS = {
    "youtube.com",
    "www.youtube.com",
    "youtu.be",
    "tiktok.com",
    "www.tiktok.com",
    "lite.tiktok.com",
    "www.lite.tiktok.com",
    "line.me",
    "linevoom.line.me",
    "www.linevoom.line.me",
    "pococha.com",
    "www.pococha.com",
    "17.live",
    "www.17.live",
    "live.nicovideo.jp",
    "www.live.nicovideo.jp",
    "nico.ms",
    "whOO.ooo",
    "www.whOO.ooo",
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

    images = MultipleFileField(
        required=False,
        label="画像（最大10枚）",
        widget=MultipleFileInput(
            attrs={
                "accept": "image/jpeg,image/png,image/webp",
            }
        ),
    )

    class Meta:
        model = Post
        fields = [
            "title",
            "body",
            "video_url",
            "video_type",
        ]

        widgets = {
            "title": forms.TextInput(
                attrs={
                    "placeholder": "タイトル"
                }
            ),

            "body": forms.Textarea(
                attrs={
                    "placeholder": "本文を入力してください",
                    "rows": 6,
                }
            ),

            "video_type": forms.RadioSelect,
        }

    def __init__(self, *args, **kwargs):

        self.user = kwargs.pop("user", None)

        super().__init__(*args, **kwargs)

    def clean_images(self):

        images = self.files.getlist("images")

        if len(images) > 10:
            raise forms.ValidationError(
                "画像は最大10枚まで投稿できます。"
            )

        allowed_types = {
            "image/jpeg",
            "image/png",
            "image/webp",
        }

        for image in images:

            if image.content_type not in allowed_types:
                raise forms.ValidationError(
                    "JPEG・PNG・WEBP形式の画像のみ投稿できます。"
                )

            if image.size > 10 * 1024 * 1024:
                raise forms.ValidationError(
                    "画像1枚の容量は10MB以下にしてください。"
                )

        return images

# =======================
# コメントフォーム
# =======================
class CommentForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = ["body", "image", "video_url", "video_type"]
        widgets = {
            "body": forms.Textarea(attrs={
                "placeholder": "コメントを書く",
                "rows": 3,
            }),
            "video_type": forms.RadioSelect
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

