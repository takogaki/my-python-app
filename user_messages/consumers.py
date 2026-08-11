import json

from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth import get_user_model
from asgiref.sync import sync_to_async
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
from django.db.models import Q
from .models import Message
from accounts.models import Match


User = get_user_model()


class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):

        user = self.scope["user"]

        # =========================
        # 🔐 未ログイン拒否
        # =========================
        if not user.is_authenticated:
            await self.close()
            return

        self.username = self.scope["url_route"]["kwargs"]["username"]

        # =========================
        # 🔐 相手ユーザー取得
        # =========================
        try:
            recipient = await sync_to_async(
                User.objects.get
            )(
                username=self.username
            )
        except User.DoesNotExist:
            await self.close()
            return

        # =========================
        # 🔥 相互LIKE（Match）確認
        # =========================
        is_matched = await sync_to_async(
            Match.objects.filter(
                Q(user1=user, user2=recipient) |
                Q(user1=recipient, user2=user)
            ).exists
        )()

        # =========================
        # ❌ Matchしていなければ接続拒否
        # =========================
        if not is_matched:
            await self.close()
            return

        # =========================
        # 🔥 ルームは必ず共通化
        # =========================
        user1 = user.username
        user2 = recipient.username

        self.room_group_name = (
            f"chat_{min(user1, user2)}_{max(user1, user2)}"
        )

        # =========================
        # 🔔 個人通知用
        # =========================
        self.user_group = f"user_{user.id}"

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.channel_layer.group_add(
            self.user_group,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):

        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

        await self.channel_layer.group_discard(
            self.user_group,
            self.channel_name
        )

    async def receive(self, text_data):

        data = json.loads(text_data)

        message_text = data.get(
            "message",
            ""
        ).strip()

        if not message_text:
            return

        sender = self.scope["user"]

        # =========================
        # 🔐 相手取得
        # =========================
        try:
            recipient = await sync_to_async(
                User.objects.get
            )(
                username=self.username
            )

        except User.DoesNotExist:
            return

        # =========================
        # 🔥 送信直前にMatch再確認
        # =========================
        is_matched = await sync_to_async(
            Match.objects.filter(
                Q(user1=sender, user2=recipient) |
                Q(user1=recipient, user2=sender)
            ).exists
        )()

        # =========================
        # ❌ LIKE解除済みなら送信拒否
        # =========================
        if not is_matched:

            await self.send(
                text_data=json.dumps({
                    "type": "error",
                    "message": "相互LIKEが解除されたため、メッセージを送信できません。",
                })
            )

            # 接続も終了
            await self.close()

            return

        # =========================
        # 💾 DB保存
        # =========================
        message = await sync_to_async(
            Message.objects.create
        )(
            sender=sender,
            recipient=recipient,
            content=message_text,
        )

        image_url = await sync_to_async(
            self.get_image_url
        )(sender)

        # =====================
        # 💬 チャット送信
        # =====================
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "id": message.id,
                "message": message.content,
                "sender": sender.username,
                "image_url": image_url,
                "sent_at": message.sent_at.isoformat(),
                "is_read": message.is_read,
            }
        )

        # =====================
        # 🔔 通知送信
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
        chat_url = (
            settings.SITE_URL
            + reverse(
                "user_messages:send_message",
                args=[sender.username]
            )
        )

        await sync_to_async(send_mail)(
            subject="【SPIRYTUS】新しいメッセージがあります",
            message=(
                f"{sender.username}さんから新しいメッセージがあります。\n\n"
                f"「{message_text}」\n\n"
                "返信はこちら\n"
                f"{chat_url}\n\n"
                "※このメールは自動送信です"
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[recipient.email],
            fail_silently=True,
        )

    # =====================
    # 💬 チャット受信
    # =====================
    async def chat_message(self, event):

        await self.send(
            text_data=json.dumps({
                "type": "chat",
                "id": event["id"],
                "message": event["message"],
                "sender": event["sender"],
                "image_url": event["image_url"],
                "sent_at": event["sent_at"],
            })
        )

    # =====================
    # 🔔 通知受信
    # =====================
    async def chat_notification(self, event):

        await self.send(
            text_data=json.dumps({
                "type": "notification",
                "event": event.get("event"),
                "sender": event.get("sender"),
                "message": event.get("message"),
                "image_url": event.get("image_url"),
            })
        )

    # =====================
    # 🖼 プロフ画像取得
    # =====================
    def get_image_url(self, user):

        profile = getattr(
            user,
            "profile",
            None
        )

        if profile and profile.profile_image:

            try:
                return profile.profile_image.url

            except Exception:
                pass

        return (
            settings.STATIC_URL
            + "accounts/img/default_avatar.png"
        )