from django.contrib import admin
from .models import Room

@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ('host', 'room_id', 'start_time', 'end_time', 'is_private')
    list_filter = ('is_private', 'start_time', 'end_time')
    search_fields = ('room_id', 'user__username') 

