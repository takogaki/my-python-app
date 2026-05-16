# accounts/middleware.py
from django.shortcuts import redirect
from django.urls import reverse
from .models import Profile

class TermsAgreementMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        # =========================
        # 🔥 絶対許可
        # =========================

        always_allowed_paths = [
            "/favicon.ico",
            "/robots.txt",
        ]

        if request.path in always_allowed_paths:
            return self.get_response(request)

        # =========================
        # 🔥 static / media許可
        # =========================

        if request.path.startswith((
            "/static/",
            "/media/",
            "/favicon.ico",
            "/robots.txt",
        )):
            return self.get_response(request)

        # =========================
        # 🔥 ログイン済のみ
        # =========================

        if request.user.is_authenticated:

            # 管理者除外
            if request.user.is_superuser:
                return self.get_response(request)

            # =========================
            # 🔥 利用規約未同意
            # =========================

            if not request.user.agreed_terms_at:

                allowed_paths = [
                    reverse("accounts:terms"),
                    reverse("accounts:logout"),
                    reverse("accounts:signup"),
                ]

                if request.method == "POST":
                    return self.get_response(request)

                if request.path not in allowed_paths:
                    return redirect("accounts:terms")

            # =========================
            # 🔥 プロフィール画像強制
            # =========================

            allowed_profile_paths = [
                reverse("accounts:profile_edit"),
                reverse("accounts:logout"),
            ]

            # admin許可
            if request.path.startswith("/admin/"):
                return self.get_response(request)

            # profile取得
            profile, created = Profile.objects.get_or_create(
                user=request.user
            )

            # 🔥 画像未設定
            if not profile.profile_image:

                if request.path not in allowed_profile_paths:
                    return redirect("accounts:profile_edit")

        return self.get_response(request)