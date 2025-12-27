# blog/validators.py

from django.core.exceptions import ValidationError
from urllib.parse import urlparse


ALLOWED_VIDEO_DOMAINS = {
    "youtube.com",
    "www.youtube.com",
    "youtu.be",
    "www.youtu.be",
    "tiktok.com",
    "www.tiktok.com",
    "instagram.com",
    "www.instagram.com",
    "facebook.com",
    "www.facebook.com",
    "fb.watch",
    "x.com",
    "www.x.com",
    "twitter.com",
    "www.twitter.com",
}


def validate_video_url(value):
    """
    動画URLが空ならOK
    ログイン必須チェックは View/Form 側で行う前提
    """
    if not value:
        return value

    parsed = urlparse(value)
    domain = parsed.netloc.lower()

    if domain not in ALLOWED_VIDEO_DOMAINS:
        raise ValidationError("許可されていない動画URLです。")

    return value