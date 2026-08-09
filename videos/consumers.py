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

    # ==================================================
    # 🔌 WebSocket接続
    # ==================================================

    async def connect(self):

        self.recruit_id = self.scope["url_route"]["kwargs"]["recruit_id"]

        self.room_group_name = (
            f"recruit_chat_{self.recruit_id}"
        )

        user = self.scope["user"]

        # ==================================================
        # 🔐 ログイン確認
        # ==================================================

        if user.is_anonymous:

            await self.close(code=4001)

            return


        # ==================================================
        # 🔐 チャット参加権限確認
        # ==================================================

        has_permission = await self.check_permission()

        if not has_permission:

            await self.close(code=4003)

            return


        # ==================================================
        # 👥 グループ参加
        # ==================================================

        await self.channel_layer.group_add(
            self.room_group_name,
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

        if hasattr(self, "room_group_name"):

            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name,
            )


    # ==================================================
    # 💬 メッセージ受信
    # ==================================================

    async def receive(self, text_data):

        # ==================================================
        # JSON解析
        # ==================================================

        try:

            data = json.loads(text_data)

        except json.JSONDecodeError:

            return


        # ==================================================
        # メッセージ取得
        # ==================================================

        text = data.get("text", "")


        if not isinstance(text, str):

            return


        text = text.strip()


        # 空メッセージ
        if not text:

            return


        # ==================================================
        # 🛡 メッセージ長制限
        # ==================================================

        text = text[:2000]


        # ==================================================
        # 👤 送信ユーザー
        # ==================================================

        user = self.scope["user"]


        # ==================================================
        # 💾 DB保存
        # ==================================================

        message = await self.save_message(
            user,
            text,
        )


        if not message:

            return


        # ==================================================
        # 👤 プロフィール画像取得
        # ==================================================

        profile_image = await self.get_profile_image(
            user
        )


        # ==================================================
        # 📡 チャット参加者全員へ配信
        # ==================================================

        await self.channel_layer.group_send(

            self.room_group_name,

            {

                "type": "chat_message",

                "username": user.username,

                "user_id": user.id,

                "profile_image": profile_image,

                "text": message.text,

                "created_at": message.created_at.strftime(
                    "%Y/%m/%d %H:%M"
                ),

            }

        )


    # ==================================================
    # 📩 グループメッセージ → クライアント
    # ==================================================

    async def chat_message(self, event):

        await self.send(

            text_data=json.dumps(

                {

                    "username": event["username"],

                    "user_id": event["user_id"],

                    "profile_image": event.get(
                        "profile_image",
                        ""
                    ),

                    "text": event["text"],

                    "created_at": event["created_at"],

                },

                ensure_ascii=False,

            )

        )


    # ==================================================
    # 👤 プロフィール画像取得
    # ==================================================

    @database_sync_to_async
    def get_profile_image(self, user):

        try:

            image = user.get_profile_image()

        except Exception:

            return ""


        if not image:

            return ""


        # ==================================================
        # get_profile_image() が
        # URLを返す現在の構成を想定
        # ==================================================

        return str(image)


    # ==================================================
    # 🔐 チャット参加権限
    # ==================================================

    @database_sync_to_async
    def check_permission(self):

        user = self.scope["user"]


        # ==================================================
        # 募集取得
        # ==================================================

        try:

            recruit = Recruit.objects.get(
                pk=self.recruit_id,
            )

        except Recruit.DoesNotExist:

            return False


        # ==================================================
        # 🏆 募集主
        #
        # 募集主は自分の募集チャットに入れる
        # ==================================================

        if recruit.user_id == user.id:

            return True


        # ==================================================
        # 👥 承認済み参加者
        # ==================================================

        return RecruitParticipant.objects.filter(

            recruit=recruit,

            user=user,

            status="approved",

        ).exists()


    # ==================================================
    # 💾 メッセージ保存
    # ==================================================

    @database_sync_to_async
    def save_message(self, user, text):

        # ==================================================
        # 募集取得
        # ==================================================

        try:

            recruit = Recruit.objects.get(
                pk=self.recruit_id,
            )

        except Recruit.DoesNotExist:

            return None


        # ==================================================
        # チャットルーム取得 / 作成
        # ==================================================

        room, created = (
            RecruitChatRoom.objects.get_or_create(
                recruit=recruit,
            )
        )


        # ==================================================
        # メッセージ保存
        # ==================================================

        return RecruitChatMessage.objects.create(

            room=room,

            user=user,

            text=text,

        )