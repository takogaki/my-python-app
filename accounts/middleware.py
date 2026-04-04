from django.shortcuts import redirect
from django.urls import reverse

class TermsAgreementMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        # 🔴 静的ファイル・メディアは通す
        if request.path.startswith("/static/") or request.path.startswith("/media/"):
            return self.get_response(request)

        # 🔴 ログイン済ユーザーのみ対象
        if request.user.is_authenticated:

            # 🔴 管理者は除外
            if request.user.is_superuser:
                return self.get_response(request)

            # 🔴 未同意ならブロック
            if not request.user.agreed_terms_at:

                allowed_paths = [
                    reverse("accounts:terms"),
                    reverse("accounts:logout"),
                    reverse("accounts:signup"),
                ]

                if request.path not in allowed_paths:
                    return redirect("accounts:terms")

        return self.get_response(request)