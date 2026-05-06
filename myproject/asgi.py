import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "myproject.settings")

django.setup()

from channels.routing import ProtocolTypeRouter, URLRouter
# myproject/asgi.py

import os
import django

from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

import user_messages.routing
import accounts.routing

application = ProtocolTypeRouter({
    "http": get_asgi_application(),

    "websocket": AuthMiddlewareStack(
        URLRouter(
            user_messages.routing.websocket_urlpatterns
            + accounts.routing.websocket_urlpatterns
        )
    ),
})