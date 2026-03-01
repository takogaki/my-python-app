"""
ASGI config for myproject project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/asgi/
"""

# myproject/asgi.py

import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "myproject.settings")

from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.core.asgi import get_asgi_application
import django

django.setup()  # ← ★これが超重要★

import user_messages.routing  # setup後に読み込む

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            user_messages.routing.websocket_urlpatterns
        )
    ),
})