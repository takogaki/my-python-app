# chat/routing.py

from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path('ws/chat/<str:room_name>/', consumers.VideoChatConsumer.as_asgi()),
]

# from django.urls import path
# from . import consumers

# websocket_urlpatterns = [
#     path('ws/chat/<str:room_name>/', consumers.ChatConsumer.as_asgi()),
# ]