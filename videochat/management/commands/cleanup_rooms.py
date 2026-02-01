from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from videochat.models import VideoRoom


class Command(BaseCommand):
    help = "6時間以上参加がないルームを自動削除（非表示）する"

    def handle(self, *args, **options):
        limit_time = timezone.now() - timedelta(hours=6)

        rooms = VideoRoom.objects.filter(
            last_joined_at__lt=limit_time,
            is_closed=False,
        )

        count = rooms.count()

        rooms.update(is_closed=True, is_live=False)

        self.stdout.write(
            self.style.SUCCESS(f"{count} 件のルームをクリーンアップしました")
        )