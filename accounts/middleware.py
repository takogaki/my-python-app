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
        # 🔥 logoutは最優先許可
        # =========================

        logout_path = reverse(
            "accounts:logout"
        ).rstrip("/")

        if current_path == logout_path:
            return self.get_response(request)

        # =========================
        # 🔥 static/media
        # =========================

        if request.path.startswith((
            "/static/",
            "/media/",
        )):
            return self.get_response(request)

        # =========================
        # 🔥 favicon等
        # =========================

        public_paths = [
            "/favicon.ico",
            "/robots.txt",
        ]

        if current_path in [
            p.rstrip("/")
            for p in public_paths
        ]:
            return self.get_response(request)

        # =========================
        # 🔥 ログイン済のみ
        # =========================

        if request.user.is_authenticated:

            # admin除外
            if (
                request.user.is_superuser
                or request.path.startswith("/admin/")
            ):
                return self.get_response(request)

            profile_edit_path = reverse(
                "accounts:profile_edit"
            ).rstrip("/")

            terms_path = reverse(
                "accounts:terms"
            ).rstrip("/")

            # =========================
            # 🔥 利用規約
            # =========================

            if not request.user.agreed_terms_at:

                if current_path != terms_path:
                    return redirect("accounts:terms")

            # =========================
            # 🔥 profile
            # =========================

            profile, created = Profile.objects.get_or_create(
                user=request.user
            )

            image_path = ""

            if profile.profile_image:
                image_path = str(profile.profile_image)

            has_real_image = (
                profile.profile_image
                and "default" not in image_path
            )

            # =========================
            # 🔥 未画像
            # =========================

            if not has_real_image:

                if current_path != profile_edit_path:
                    return redirect("accounts:profile_edit")

        return self.get_response(request)