import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth import get_user_model
from asgiref.sync import sync_to_async
from .models import Message
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse

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

        self.user_group = f"user_{self.scope['user'].id}"

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.channel_layer.group_add(self.user_group, self.channel_name)

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
        await self.channel_layer.group_discard(self.user_group, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        message_text = data["message"]

        sender = self.scope["user"]
        recipient = await sync_to_async(User.objects.filter(username=self.username).first)()
        if not recipient:
            return

        message = await sync_to_async(Message.objects.create)(
            sender=sender,
            recipient=recipient,
            content=message_text,
        )

        image_url = await sync_to_async(self.get_image_url)(sender)
        user = await sync_to_async(User.objects.get)(pk=self.scope["user"].pk)

        # =====================
        # 💬 チャット送信
        # =====================
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "id": message.id,
                "message": message.content,
                "sender": user.username,
                "image_url": image_url,
                "sent_at": str(message.sent_at),
            }
        )

        # =====================
        # 🔔 通知送信（重要）
        # =====================
        await self.channel_layer.group_send(
            f"user_{recipient.id}",
            {
                "type": "chat_notification",
                "event": "message",
                "sender": sender.username,
                "message": message_text,
                "image_url": image_url,
            }
        )

        # =====================
        # 📧 メール通知
        # =====================
        chat_url = settings.SITE_URL + reverse(
            "user_messages:send_message",
            args=[sender.username]
        )

        await sync_to_async(send_mail)(
            subject="【SPIRYTUS】新しいメッセージがあります",
            message=(
                f"{sender.username}さんから新しいメッセージがあります。\n\n"
                f"「{message_text}」\n\n"
                "返信はこちらから\n"
                f"{chat_url}\n\n"
                "※このメールは自動送信です\n"
                "※このメールに返信することはできません"
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[recipient.email],
            fail_silently=True,
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            "id": event["id"],
            "message": event["message"],
            "sender": event["sender"],
            "image_url": event["image_url"],
            "sent_at": event["sent_at"],
        }))

    async def chat_notification(self, event):
        await self.send(text_data=json.dumps({
            "type": "notification",
            "event": event.get("event"),
            "sender": event.get("sender"),
            "message": event.get("message"),
            "image_url": event.get("image_url"),
        }))

    def get_image_url(self, user):
        profile = getattr(user, "profile", None)

        if profile and profile.profile_image:
            try:
                return profile.profile_image.url
            except:
                pass

        return settings.STATIC_URL + "accounts/img/default_avatar.png"