# videochat/consumers.py

from channels.generic.websocket import AsyncJsonWebsocketConsumer


class LiveRoomConsumer(AsyncJsonWebsocketConsumer):
    """
    SPIRYTUS LIVE

    ・LIVEルーム接続
    ・WebRTCシグナリング
    ・コメント
    ・視聴者参加/退出
    ・音声/映像参加リクエスト
    """

    async def connect(self):

        self.room_slug = (
            self.scope["url_route"]["kwargs"]["room_slug"]
        )

        self.room_group_name = (
            f"live_room_{self.room_slug}"
        )

        user = self.scope.get("user")

        if not user or not user.is_authenticated:

            await self.close(code=4001)

            return


        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name,
        )


        await self.accept()


        # ------------------------------------------
        # 接続完了
        # ------------------------------------------

        await self.send_json({
            "type": "connection_info",
            "channel_name": self.channel_name,
            "user_id": user.id,
            "username": user.username,
        })


        # ------------------------------------------
        # 他ユーザーへ参加通知
        # ------------------------------------------

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "live_system",
                "event": "viewer_joined",

                "channel_name":
                    self.channel_name,

                "user_id":
                    user.id,

                "username":
                    user.username,
            },
        )


    async def disconnect(
        self,
        close_code
    ):

        if not hasattr(
            self,
            "room_group_name"
        ):

            return


        user = self.scope.get("user")


        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name,
        )


        if user and user.is_authenticated:

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "live_system",
                    "event": "viewer_left",

                    "channel_name":
                        self.channel_name,

                    "user_id":
                        user.id,

                    "username":
                        user.username,
                },
            )


    # ==================================================
    # Receive
    # ==================================================

    async def receive_json(
        self,
        content,
        **kwargs
    ):

        message_type = content.get("type")


        # ==================================================
        # WebRTC Offer / Answer / ICE
        # ==================================================

        if message_type in {
            "offer",
            "answer",
            "ice-candidate",
        }:

            target_channel = (
                content.get(
                    "target_channel"
                )
            )


            if not target_channel:

                return


            await self.channel_layer.send(
                target_channel,
                {
                    "type":
                        "webrtc_signal",

                    "message": {
                        **content,

                        "sender_channel":
                            self.channel_name,
                    },
                },
            )

            return


        # ==================================================
        # コメント
        # ==================================================

        if message_type == "comment":

            user = self.scope["user"]

            text = str(
                content.get(
                    "text",
                    ""
                )
            ).strip()


            if not text:

                return


            text = text[:300]


            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type":
                        "live_comment",

                    "username":
                        user.username,

                    "user_id":
                        user.id,

                    "text":
                        text,
                },
            )

            return


        # ==================================================
        # 音声参加リクエスト
        # ==================================================

        if message_type == "request_audio":

            user = self.scope["user"]


            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type":
                        "participant_request",

                    "request_type":
                        "audio",

                    "username":
                        user.username,

                    "user_id":
                        user.id,

                    "channel_name":
                        self.channel_name,
                },
            )

            return


        # ==================================================
        # 映像参加リクエスト
        # ==================================================

        if message_type == "request_video":

            user = self.scope["user"]


            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type":
                        "participant_request",

                    "request_type":
                        "video",

                    "username":
                        user.username,

                    "user_id":
                        user.id,
                },
            )

            return


        # ==================================================
        # LIVE終了
        # ==================================================

        if message_type == "end_live":

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type":
                        "live_system",

                    "event":
                        "live_ended",
                },
            )

            return


    # ==================================================
    # WebRTC signal
    # ==================================================

    async def webrtc_signal(
        self,
        event
    ):

        message = event["message"]


        await self.send_json(
            message
        )


    # ==================================================
    # コメント
    # ==================================================

    async def live_comment(
        self,
        event
    ):

        await self.send_json({

            "type":
                "comment",

            "username":
                event["username"],

            "user_id":
                event["user_id"],

            "text":
                event["text"],

        })


    # ==================================================
    # 参加リクエスト
    # ==================================================

    async def participant_request(
        self,
        event
    ):

        await self.send_json({

            "type":
                "participant_request",

            "request_type":
                event["request_type"],

            "username":
                event["username"],

            "user_id":
                event["user_id"],

        })


    # ==================================================
    # システムイベント
    # ==================================================

    async def live_system(
        self,
        event
    ):

        await self.send_json({

            "type":
                "live_system",

            "event":
                event.get(
                    "event"
                ),

            "channel_name":
                event.get(
                    "channel_name"
                ),

            "user_id":
                event.get(
                    "user_id"
                ),

            "username":
                event.get(
                    "username"
                ),

        })