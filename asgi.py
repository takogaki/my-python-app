# myproject/asgi.py
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import user_messages.routing   # ← ここ変更

application = ProtocolTypeRouter({
    'http': get_asgi_application(),
    'websocket': AuthMiddlewareStack(
        URLRouter(
            user_messages.routing.websocket_urlpatterns  # ← ここも変更
        )
    ),
})