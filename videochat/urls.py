from django.urls import path
from . import views
# テスト用
from .views import jitsi_test

app_name = "videochat"

urlpatterns = [
    # テスト用
    path("jitsi-test/", jitsi_test, name="jitsi_test"),

    path("", views.room_list, name="room_list"),
    path("create/", views.room_create, name="room_create"),
    path("<slug:room_slug>/", views.room_detail, name="room_detail"),
    path("<slug:room_slug>/join/", views.room_join, name="room_join"),
    path("<slug:room_slug>/start/", views.room_start, name="room_start"),
    #配信開始用 
    path("start/", views.start_room, name="start"),
    path("room/<uuid:room_id>/", views.room_detail, name="room"),
]