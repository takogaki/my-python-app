from django.urls import path
from . import views

app_name = "user_messages"

urlpatterns = [
    path("send_message/<str:username>/", views.send_message, name="send_message"),
    path("success/", views.success, name="success"),
    path("message_box/", views.message_box, name="message_box"),
    path("failure/", views.failure, name="failure"),

]