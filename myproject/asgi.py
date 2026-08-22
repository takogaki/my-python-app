import os
import django

from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.core.asgi import get_asgi_application


os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "myproject.settings"
)

django.setup()


import user_messages.routing
import accounts.routing
import videos.routing
import random_call.routing


application = ProtocolTypeRouter({

    "http": get_asgi_application(),

    "websocket": AuthMiddlewareStack(
        URLRouter(

            # 通常DM
            user_messages.routing.websocket_urlpatterns

            +

            # accounts関連WebSocket
            accounts.routing.websocket_urlpatterns

            +

            # 募集チャット
            videos.routing.websocket_urlpatterns

            +

            # ランダム通話
            random_call.routing.websocket_urlpatterns

        )
    ),
})