from django.urls import re_path

from .consumers import RandomCallConsumer


websocket_urlpatterns = [
    re_path(
        r"ws/random-call/$",
        RandomCallConsumer.as_asgi(),
    ),
]