import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth import get_user_model
from asgiref.sync import sync_to_async
from .models import Message

User = get_user_model()


class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        if not self.scope["user"].is_authenticated:
            await self.close()
            return

        self.username = self.scope["url_route"]["kwargs"]["username"]

        user1 = self.scope["user"].username
        user2 = self.username
        self.room_name = f"chat_{min(user1, user2)}_{max(user1, user2)}"
        self.room_group_name = self.room_name

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        # print("🔥 receive called")

        data = json.loads(text_data)
        message_text = data["message"]

        sender = self.scope["user"]
        recipient = await sync_to_async(User.objects.get)(username=self.username)

        message = await sync_to_async(Message.objects.create)(
            sender=sender,
            recipient=recipient,
            content=message_text,
        )

        image_url = await sync_to_async(self.get_image_url)(sender)

        # 🔥 ここで毎回取り直す
        user = await sync_to_async(User.objects.get)(pk=self.scope["user"].pk)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "message": message.content,
                "sender": user.username,
                "image_url": user.profile_image.url if user.profile_image else "",
            }
        )

    async def chat_message(self, event):
        # print("🔥 chat_message called")
        await self.send(text_data=json.dumps({
            "message": event["message"],
            "sender": event["sender"],
            "image_url": event["image_url"],
        }))

    def get_image_url(self, user):
        profile = getattr(user, "profile", None)
        if not profile:
            return ""

        image = getattr(profile, "profile_image", None)
        if image and hasattr(image, "url"):
            return image.url

        return ""