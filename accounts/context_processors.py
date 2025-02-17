# accounts/context_processors.py
from myproject.middleware import VisitorTrackingMiddleware

def visitor_counts(request):
    active_visitors = VisitorTrackingMiddleware.get_active_visitors_count()
    logged_in_users = VisitorTrackingMiddleware.get_logged_in_users_count()
    return {
        'active_visitors_count': active_visitors,
        'logged_in_users_count': logged_in_users,
    }