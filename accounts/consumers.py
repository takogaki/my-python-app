# accounts/consumers.py

import json

from channels.generic.websocket import AsyncWebsocketConsumer


class NotificationConsumer(AsyncWebsocketConsumer):

    # ==================================================
    # 🔌 WebSocket接続
    # ==================================================

    async def connect(self):

        user = self.scope["user"]

        # ==================================================
        # 🔐 ログイン確認
        # ==================================================

        if not user.is_authenticated:
            await self.close(code=4001)
            return

        # ==================================================
        # 👤 ユーザー専用通知グループ
        # ==================================================

        self.group_name = f"user_{user.id}"

        # ==================================================
        # 👥 グループ参加
        # ==================================================

        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name,
        )

        # ==================================================
        # 🟢 接続許可
        # ==================================================

        await self.accept()


    # ==================================================
    # 🔌 WebSocket切断
    # ==================================================

    async def disconnect(self, close_code):

        # group_name が存在する場合のみ退出
        if hasattr(self, "group_name"):

            await self.channel_layer.group_discard(
                self.group_name,
                self.channel_name,
            )


    # ==================================================
    # 🔔 通知受信
    # ==================================================

    async def chat_notification(self, event):

        await self.send(
            text_data=json.dumps(
                {
                    "type": "notification",

                    "event": event.get(
                        "event"
                    ),

                    "sender": event.get(
                        "sender"
                    ),

                    "message": event.get(
                        "message"
                    ),

                    "image_url": event.get(
                        "image_url"
                    ),
                },

                ensure_ascii=False,
            )
        )