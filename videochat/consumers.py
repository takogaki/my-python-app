from channels.generic.websocket import AsyncJsonWebsocketConsumer


class LiveRoomConsumer(AsyncJsonWebsocketConsumer):
    """
    SPIRYTUS LIVE

    ・LIVEルーム接続
    ・WebRTCシグナリング
    ・コメント
    ・視聴者参加/退出
    ・音声/映像参加リクエスト
    ・参加許可
    ・LIVE終了
    """

    # ==================================================
    # Connect
    # ==================================================

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


        # ------------------------------------------
        # WebSocket Group
        # ------------------------------------------

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name,
        )


        await self.accept()


        # ------------------------------------------
        # 自分の接続情報
        # ------------------------------------------

        await self.send_json({

            "type":
                "connection_info",

            "channel_name":
                self.channel_name,

            "user_id":
                user.id,

            "username":
                user.username,

        })


        # ------------------------------------------
        # 他ユーザーへ参加通知
        # ------------------------------------------

        await self.channel_layer.group_send(
            self.room_group_name,
            {

                "type":
                    "live_system",

                "event":
                    "viewer_joined",

                "channel_name":
                    self.channel_name,

                "user_id":
                    user.id,

                "username":
                    user.username,

            },
        )


    # ==================================================
    # Disconnect
    # ==================================================

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

                    "type":
                        "live_system",

                    "event":
                        "viewer_left",

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

        user = self.scope.get("user")


        if not user or not user.is_authenticated:

            return


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

                    "channel_name":
                        self.channel_name,

                },
            )

            return


        # ==================================================
        # 現在の視聴者情報要求
        # ==================================================

        if message_type == "request_viewers":

            await self.send_current_viewers()

            return


        # ==================================================
        # 参加許可
        # ==================================================

        if message_type == "approve_participation":

            target_channel = (
                content.get(
                    "target_channel"
                )
            )

            participation_type = (
                content.get(
                    "participation_type"
                )
            )


            if not target_channel:

                return


            if participation_type not in {
                "audio",
                "video",
            }:

                return


            # ------------------------------------------
            # 許可した視聴者へ直接通知
            # ------------------------------------------

            await self.channel_layer.send(
                target_channel,
                {

                    "type":
                        "participation_approved",

                    "message": {

                        "type":
                            "participation_approved",

                        "participation_type":
                            participation_type,

                        "host_channel":
                            self.channel_name,

                    },

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
    # Current viewers
    # ==================================================

    async def send_current_viewers(self):

        """
        現在の視聴者一覧。

        ChannelsのGroup自体からメンバー一覧を取得する
        ことはできないため、現在は補助的に使用。
        """

        await self.send_json({

            "type":
                "current_viewers",

            "viewers":
                [],

        })


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
    # Participation approved
    # ==================================================

    async def participation_approved(
        self,
        event
    ):

        message = event["message"]


        await self.send_json(
            message
        )


    # ==================================================
    # Comment
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
    # Participant request
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

            "channel_name":
                event.get(
                    "channel_name"
                ),

        })


    # ==================================================
    # System event
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