# blog/validators.py
from django.conf import settings
from urllib.parse import urlparse
from django.core.exceptions import ValidationError


def validate_video_url(value):
    if not value:
        return value

    parsed = urlparse(value)
    domain = parsed.netloc.lower()

    # サブドメイン対応
    if not any(allowed in domain for allowed in settings.ALLOWED_VIDEO_DOMAINS):
        raise ValidationError("許可されていない動画URLです。")

    return value