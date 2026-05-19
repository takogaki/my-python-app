# accounts/middleware.py

from django.shortcuts import redirect
from django.urls import reverse
from .models import Profile


class TermsAgreementMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        current_path = request.path.rstrip("/")

        # =========================
        # 🔥 static/media許可
        # =========================

        if request.path.startswith((
            "/static/",
            "/media/",
        )):
            return self.get_response(request)

        # =========================
        # 🔥 favicon等
        # =========================

        allowed_public_paths = [
            "/favicon.ico",
            "/robots.txt",
        ]

        if current_path in [
            p.rstrip("/")
            for p in allowed_public_paths
        ]:
            return self.get_response(request)

        # =========================
        # 🔥 ログイン済のみ
        # =========================

        if request.user.is_authenticated:

            # =========================
            # 🔥 admin除外
            # =========================

            if (
                request.user.is_superuser
                or request.path.startswith("/admin/")
            ):
                return self.get_response(request)

            # =========================
            # 🔥 共通許可ページ
            # =========================

            common_allowed_paths = [
                reverse("accounts:logout").rstrip("/"),
                reverse("accounts:profile_edit").rstrip("/"),
                reverse("accounts:terms").rstrip("/"),
            ]

            # POSTは絶対許可
            if request.method == "POST":
                return self.get_response(request)

            # =========================
            # 🔥 利用規約チェック
            # =========================

            if not request.user.agreed_terms_at:

                if current_path not in common_allowed_paths:
                    return redirect("accounts:terms")

            # =========================
            # 🔥 画像チェック
            # =========================

            profile, created = Profile.objects.get_or_create(
                user=request.user
            )

            has_real_image = (
                profile.profile_image
                and "default" not in str(profile.profile_image)
            )

            if not has_real_image:

                if current_path not in common_allowed_paths:
                    return redirect("accounts:profile_edit")

        return self.get_response(request)