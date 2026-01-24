from django.urls import path, include
from . import views

app_name = "notifications"

urlpatterns = [
    path("read/<int:pk>/", views.notification_read, name="read"),
    # project/urls.py
    path("notifications/", include("notifications.urls")),
    path("open/<int:pk>/", views.open_notification, name="open_notification"),
]