import json

from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async

from .models import (
    Recruit,
    RecruitParticipant,
    RecruitChatRoom,
    RecruitChatMessage,
)


class RecruitChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):

        self.recruit_id = self.scope["url_route"]["kwargs"]["recruit_id"]

        self.room_group_name = f"recruit_chat_{self.recruit_id}"

        # =========================
        # 🔐 ログイン確認
        # =========================

        if self.scope["user"].is_anonymous:
            await self.close(code=4001)
            return

        # =========================
        # 🔐 チャット参加権限確認
        # =========================

        has_permission = await self.check_permission()

        if not has_permission:
            await self.close(code=4003)
            return

        # =========================
        # 👥 グループ参加
        # =========================

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name,
        )

        await self.accept()

    async def disconnect(self, close_code):

        if hasattr(self, "room_group_name"):

            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name,
            )

    # =========================
    # 💬 メッセージ受信
    # =========================

    async def receive(self, text_data):

        try:
            data = json.loads(text_data)
        except json.JSONDecodeError:
            return

        text = data.get("text", "").strip()

        if not text:
            return

        # 長すぎるメッセージを防止
        text = text[:2000]

        user = self.scope["user"]

        # =========================
        # 💾 DB保存
        # =========================

        message = await self.save_message(
            user,
            text,
        )

        if not message:
            return

        # =========================
        # 📡 全参加者へ配信
        # =========================

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "username": user.username,
                "text": message.text,
                "created_at": message.created_at.strftime(
                    "%Y/%m/%d %H:%M"
                ),
                "user_id": user.id,
            },
        )

    # =========================
    # 📩 クライアントへ送信
    # =========================

    async def chat_message(self, event):

        await self.send(
            text_data=json.dumps(
                {
                    "username": event["username"],
                    "text": event["text"],
                    "created_at": event["created_at"],
                    "user_id": event["user_id"],
                },
                ensure_ascii=False,
            )
        )

    # =========================
    # 🔐 権限確認
    # =========================

    @database_sync_to_async
    def check_permission(self):

        user = self.scope["user"]

        try:
            recruit = Recruit.objects.get(
                pk=self.recruit_id,
                is_active=True,
            )
        except Recruit.DoesNotExist:
            return False

        # 募集主
        if recruit.user_id == user.id:
            return True

        # 承認済み参加者のみ
        return RecruitParticipant.objects.filter(
            recruit=recruit,
            user=user,
            status="approved",
        ).exists()

    # =========================
    # 💾 メッセージ保存
    # =========================

    @database_sync_to_async
    def save_message(self, user, text):

        try:
            recruit = Recruit.objects.get(
                pk=self.recruit_id,
                is_active=True,
            )
        except Recruit.DoesNotExist:
            return None

        room, created = RecruitChatRoom.objects.get_or_create(
            recruit=recruit,
        )

        return RecruitChatMessage.objects.create(
            room=room,
            user=user,
            text=text,
        )