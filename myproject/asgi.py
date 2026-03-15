import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "myproject.settings")

django.setup()

from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.core.asgi import get_asgi_application
import user_messages.routing

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            user_messages.routing.websocket_urlpatterns
        )
    ),
})