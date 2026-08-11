from django.core.cache import cache

from myproject.middleware import VisitorTrackingMiddleware

from .models import CustomUser
from notifications.models import Notification


# =========================
# 👤 登録ユーザー数
# =========================

def user_count(request):

    count = cache.get("user_count")

    if count is None:
        count = CustomUser.objects.filter(
            is_active=True
        ).count()

        cache.set(
            "user_count",
            count,
            60
        )

    return {
        "user_count": count
    }


# =========================
# 👀 アクティブユーザー数
# =========================

def visitor_counts(request):

    active_visitors = (
        VisitorTrackingMiddleware
        .get_active_visitors_count()
    )

    logged_in_users = (
        VisitorTrackingMiddleware
        .get_logged_in_users_count()
    )

    return {
        "active_visitors_count": active_visitors,
        "logged_in_users_count": logged_in_users,
    }


# =========================
# 🔔 通知未読件数
# =========================

def notification_unread_count(request):

    if not request.user.is_authenticated:
        return {
            "notification_unread_total": 0
        }

    notification_unread_total = Notification.objects.filter(
        recipient=request.user,
        is_read=False,
        type__in=[
            "tag_match",
            "footprint",
            "like",
            "match",
            "message",
        ],
    ).count()

    return {
        "notification_unread_total": notification_unread_total
    }