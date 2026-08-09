import json

from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async

from django.core.mail import send_mail
from django.conf import settings

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

        self.recruit_id = (
            self.scope["url_route"]["kwargs"]["recruit_id"]
        )

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

        has_permission = (
            await self.check_permission()
        )

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

        if hasattr(
            self,
            "room_group_name"
        ):

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

        text = data.get(
            "text",
            ""
        )

        if not isinstance(
            text,
            str
        ):

            return

        text = text.strip()

        # ==================================================
        # 空メッセージ
        # ==================================================

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
        # 📧 メール通知
        #
        # チャットへの配信とは独立して処理
        # ==================================================

        await self.send_email_notification(
            user,
            message,
        )

        # ==================================================
        # 👤 プロフィール画像取得
        # ==================================================

        profile_image = (
            await self.get_profile_image(
                user
            )
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

                "is_superuser": user.is_superuser,

                "text": message.text,

                "created_at": (
                    message.created_at.strftime(
                        "%Y/%m/%d %H:%M"
                    )
                ),

            }

        )

    # ==================================================
    # 📩 グループメッセージ
    # → クライアント
    # ==================================================

    async def chat_message(
        self,
        event
    ):

        await self.send(

            text_data=json.dumps(

                {

                    "username": (
                        event["username"]
                    ),

                    "user_id": (
                        event["user_id"]
                    ),

                    "profile_image": (
                        event.get(
                            "profile_image",
                            ""
                        )
                    ),

                    "is_superuser": (
                        event.get(
                            "is_superuser",
                            False
                        )
                    ),

                    "text": (
                        event["text"]
                    ),

                    "created_at": (
                        event["created_at"]
                    ),

                },

                ensure_ascii=False,

            )

        )

    # ==================================================
    # 📧 メール通知
    # ==================================================

    @database_sync_to_async
    def send_email_notification(
        self,
        sender,
        message,
    ):

        try:

            # ==================================================
            # 募集取得
            # ==================================================

            recruit = (
                Recruit.objects.select_related(
                    "user"
                ).get(
                    pk=self.recruit_id
                )
            )

            # ==================================================
            # 通知先
            # ==================================================

            recipients = []

            # ==================================================
            # 募集主から送信
            #
            # → 承認済み応募者全員
            # ==================================================

            if recruit.user_id == sender.id:

                participants = (
                    RecruitParticipant.objects
                    .filter(
                        recruit=recruit,
                        status="approved",
                    )
                    .select_related("user")
                )

                for participant in participants:

                    user = participant.user

                    if user.id == sender.id:
                        continue

                    if not user.email:
                        continue

                    recipients.append(
                        user.email
                    )

            # ==================================================
            # 応募者から送信
            #
            # → 募集主
            # ==================================================

            else:

                if (
                    recruit.user.email
                    and recruit.user_id != sender.id
                ):

                    recipients.append(
                        recruit.user.email
                    )

            # ==================================================
            # 通知先なし
            # ==================================================

            if not recipients:

                return

            # ==================================================
            # 重複削除
            # ==================================================

            recipients = list(
                dict.fromkeys(
                    recipients
                )
            )

            # ==================================================
            # チャットURL
            #
            # 現在のURL構成に合わせる
            # ==================================================

            site_url = getattr(
                settings,
                "SITE_URL",
                ""
            ).rstrip("/")

            chat_url = (
                f"{site_url}"
                f"/videos/recruit/"
                f"{self.recruit_id}/chat/"
            )

            # ==================================================
            # メール件名
            # ==================================================

            subject = (
                f"【SPIRYTUS】"
                f"{recruit.title}"
                f"に新しいメッセージがあります"
            )

            # ==================================================
            # メール本文
            # ==================================================

            body = (
                f"{sender.username} さんから"
                f"募集チャットに新しいメッセージがあります。\n\n"

                f"募集：\n"
                f"{recruit.title}\n\n"

                f"送信者：\n"
                f"{sender.username}\n\n"

                f"メッセージ：\n"
                f"{message.text}\n\n"
            )

            if chat_url:

                body += (
                    "チャットを確認する：\n"
                    f"{chat_url}\n\n"
                )

            body += (
                "※このメールはSPIRYTUSの"
                "募集チャット通知です。"
            )

            # ==================================================
            # 送信
            # ==================================================

            send_mail(

                subject=subject,

                message=body,

                from_email=getattr(
                    settings,
                    "DEFAULT_FROM_EMAIL",
                    None
                ),

                recipient_list=recipients,

                fail_silently=True,

            )

        except Exception:

            # ==================================================
            # メールエラーで
            # チャットを止めない
            # ==================================================

            return

    # ==================================================
    # 👤 プロフィール画像取得
    # ==================================================

    @database_sync_to_async
    def get_profile_image(
        self,
        user
    ):

        try:

            image = (
                user.get_profile_image()
            )

        except Exception:

            return ""

        if not image:

            return ""

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

            recruit = (
                Recruit.objects.get(
                    pk=self.recruit_id
                )
            )

        except Recruit.DoesNotExist:

            return False

        # ==================================================
        # 🏆 募集主
        # ==================================================

        if recruit.user_id == user.id:

            return True

        # ==================================================
        # 👥 承認済み参加者
        # ==================================================

        return (
            RecruitParticipant.objects.filter(

                recruit=recruit,

                user=user,

                status="approved",

            ).exists()
        )

    # ==================================================
    # 💾 メッセージ保存
    # ==================================================

    @database_sync_to_async
    def save_message(
        self,
        user,
        text
    ):

        # ==================================================
        # 募集取得
        # ==================================================

        try:

            recruit = (
                Recruit.objects.get(
                    pk=self.recruit_id
                )
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

        return (
            RecruitChatMessage.objects.create(

                room=room,

                user=user,

                text=text,

            )
        )