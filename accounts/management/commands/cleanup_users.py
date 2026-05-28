from django.core.management.base import BaseCommand
from django.utils import timezone
from django.utils.timezone import make_aware
from django.core.mail import send_mail
from django.db.models import Q

from datetime import timedelta, datetime

from accounts.models import CustomUser


class Command(BaseCommand):
    help = "未設定プロフィール画像ユーザー整理"

    def handle(self, *args, **kwargs):

        # =========================
        # 写真必須化した日
        # 2026/5/1以降は
        # 新規登録時にプロフィール画像必須化済み
        # それ以前ユーザーのみ整理対象
        # =========================
        PHOTO_REQUIRED_DATE = make_aware(
            datetime(2026, 5, 1)
        )

        now = timezone.now()

        # =========================
        # 警告メール送信
        # =========================
        warning_users = CustomUser.objects.filter(
            date_joined__lt=PHOTO_REQUIRED_DATE,
            profile__warning_mail_sent=False,
        ).filter(
            Q(profile__profile_image="") |
            Q(profile__profile_image__isnull=True)
        )

        for user in warning_users:

            if user.email:

                send_mail(
                    subject="プロフィール画像未設定のお知らせ",
                    message="""
プロフィール画像が未設定です。

7日後にアカウントが自動削除されます。

引き続きご利用される場合は、
プロフィール画像を設定してください。
""",
                    from_email="diary.message999@gmail.com",
                    recipient_list=[user.email],
                    fail_silently=True,
                )

            # =========================
            # 警告日時保存
            # =========================
            user.profile.warning_mail_sent = True
            user.profile.warning_sent_at = now
            user.profile.save()

            self.stdout.write(
                self.style.WARNING(
                    f"警告メール送信: {user.username}"
                )
            )

        # =========================
        # 7日後 → 削除
        # =========================
        delete_date = now - timedelta(days=7)

        delete_users = CustomUser.objects.filter(
            date_joined__lt=PHOTO_REQUIRED_DATE,
            profile__warning_mail_sent=True,
            profile__warning_sent_at__lt=delete_date,
        ).filter(
            Q(profile__profile_image="") |
            Q(profile__profile_image__isnull=True)
        )

        for user in delete_users:

            username = user.username

            # 最初はコメントアウト推奨
            user.delete()

            self.stdout.write(
                self.style.ERROR(
                    f"削除対象: {username}"
                )
            )