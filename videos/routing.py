from django.urls import re_path

from .consumers import RecruitChatConsumer


websocket_urlpatterns = [
    re_path(
        r"ws/recruit/(?P<recruit_id>\d+)/$",
        RecruitChatConsumer.as_asgi(),
    ),
]