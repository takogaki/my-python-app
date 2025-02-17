from django.utils.deprecation import MiddlewareMixin
from django.contrib.sessions.models import Session
from django.contrib.auth import get_user_model
from datetime import datetime


User = get_user_model()

class VisitorTrackingMiddleware(MiddlewareMixin):
    def process_request(self, request):
        # セッションがない場合は新規作成
        session_key = request.session.session_key
        if not session_key:
            request.session.create()

    @staticmethod
    def get_active_visitors_count():
        # アクティブなセッション数を取得
        return Session.objects.filter(expire_date__gt=datetime.now()).count()

    @staticmethod
    def get_logged_in_users_count():
        # 現在ログインしているユーザーの数を取得
        active_sessions = Session.objects.filter(expire_date__gt=datetime.now())
        logged_in_users = User.objects.filter(
            id__in=[session.get_decoded().get('_auth_user_id') for session in active_sessions]
        )
        return logged_in_users.count()