from django.urls import path
from . import views

app_name = "notifications"

urlpatterns = [
    # project/urls.py
    path("open/<int:pk>/", views.open_notification, name="open_notification"),
]