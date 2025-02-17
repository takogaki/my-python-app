from django.contrib import admin
from .models import Message

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("sender", "recipient", "sent_at", "is_read", "is_important")
    list_filter = ("is_read", "is_important", "sent_at")
    search_fields = ("sender__username", "recipient__username", "content")
    ordering = ("-sent_at",)

# または以下のシンプルな書き方
# admin.site.register(Message)