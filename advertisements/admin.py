from django.contrib import admin
from .models import Advertisement


@admin.register(Advertisement)
class AdvertisementAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "placement",
        "is_active",
        "created_at",
    )

    list_filter = (
        "placement",
        "is_active",
    )

    search_fields = (
        "name",
    )