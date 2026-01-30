from django.urls import path
from . import views
from .views import jitsi_test

app_name = "videochat"

urlpatterns = [
    # テスト用（環境確認）
    path("jitsi-test/", jitsi_test, name="jitsi_test"),
    
    path("", views.room_list, name="room_list"),
    path("start/", views.start_room, name="start"),
    path("<slug:room_slug>/start/", views.room_start, name="room_start"),
    path("<slug:room_slug>/join/", views.room_join, name="room_join"),
    path("join/<slug:room_slug>/", views.room_join, name="room_join"),
    path("videochat/<slug:room_slug>/heartbeat/", views.room_heartbeat, name="room_heartbeat"),
    path("<slug:room_slug>/manage/", views.room_manage, name="room_manage"),
    path("<slug:room_slug>/approve/<int:user_id>/", views.approve_participant, name="approve_participant"),
    path("<slug:room_slug>/end/", views.room_end, name="room_end"),
]