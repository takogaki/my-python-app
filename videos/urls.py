from django.urls import path
from . import views

urlpatterns = [
    path("feed/", views.feed, name="feed"),
    path("upload/", views.upload, name="video_upload")
]