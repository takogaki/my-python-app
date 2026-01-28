from django.urls import path
from . import views
from .views import jitsi_test

app_name = "videochat"

urlpatterns = [
    path("jitsi-test/", jitsi_test, name="jitsi_test"),
    path("", views.room_list, name="room_list"),
    path("start/", views.start_room, name="start"),
    path("<slug:room_slug>/start/", views.room_start, name="room_start"),
    path("<slug:room_slug>/join/", views.room_join, name="room_join"),
]