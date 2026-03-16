from django.core.cache import cache
from myproject.middleware import VisitorTrackingMiddleware
from .models import CustomUser


def user_count(request):
    count = cache.get("user_count")

    if count is None:
        count = CustomUser.objects.filter(is_active=True).count()
        cache.set("user_count", count, 60)  # 60秒キャッシュ

    return {"user_count": count}


def visitor_counts(request):
    active_visitors = VisitorTrackingMiddleware.get_active_visitors_count()
    logged_in_users = VisitorTrackingMiddleware.get_logged_in_users_count()

    return {
        "active_visitors_count": active_visitors,
        "logged_in_users_count": logged_in_users,
    }