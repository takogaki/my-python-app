# blog/templatetags/youtube_extras.py

import re
from django import template

register = template.Library()


@register.filter
def youtube_id(url):
    """
    YouTube URL から動画IDを抜き出す
    """
    if not url:
        return ""

    patterns = [
        r"youtube\.be/([^?&/]+)",
        r"youtube\.com/watch\?v=([^?&/]+)",
        r"youtube\.com/embed/([^?&/]+)",
    ]

    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)

    return ""