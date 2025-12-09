from django.core.management.base import BaseCommand
from django.db import transaction
from blog.models import Post

class Command(BaseCommand):
    help = "Fix posts with slug='-1' by clearing slug so model.save() regenerates it."

    def handle(self, *args, **options):
        bad_qs = Post.objects.filter(slug='-1')
        self.stdout.write(f"Found {bad_qs.count()} posts with slug='-1'.")
        if bad_qs.count() == 0:
            return

        confirm = input("Proceed to fix these posts? (y/N): ").lower()
        if confirm != 'y':
            self.stdout.write("Aborted.")
            return

        with transaction.atomic():
            for p in bad_qs:
                old = p.slug
                p.slug = ''
                p.save()
                self.stdout.write(f"Updated id={p.id} '{p.title}': {old} -> {p.slug}")

        self.stdout.write("Done.")
