import uuid

from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django.conf import settings
from redis.asyncio import Redis


# ==================================================
# Redis 待機キュー
# ==================================================

WAITING_MALE = "random_call:waiting:male"
WAITING_FEMALE = "random_call:waiting:female"
WAITING_OTHER = "random_call:waiting:other"


# ==================================================
# Redis 接続状態
#
# user_id → connection token
#
# これにより、
# 「現在WebSocket接続しているユーザー」
# を確認できるようにする。
# ==================================================

CONNECTED_USER_PREFIX = "random_call:connected:"
CONNECTED_TTL = 60


class RandomCallConsumer(AsyncJsonWebsocketConsumer):

    # ==================================================
    # WebSocket 接続
    # ==================================================

    async def connect(self):

        self.user = self.scope["user"]
        self.call_id = None
        self.is_waiting = False

        # このWebSocket固有のID
        self.connection_token = str(uuid.uuid4())

        # --------------------------------------------------
        # 未ログイン
        # --------------------------------------------------

        if not self.user.is_authenticated:

            await self.close(code=4001)
            return

        # --------------------------------------------------
        # 性別
        # --------------------------------------------------

        self.gender = self.user.gender

        if self.gender not in ["M", "F", "O"]:

            await self.accept()

            await self.send_json({
                "type": "gender_not_supported",
                "message": "性別を設定しているユーザーのみ利用できます。",
            })

            await self.close(code=4003)
            return

        # ==================================================
        # Redis 接続
        # ==================================================

        redis_url = getattr(settings, "REDIS_URL", None)

        if not redis_url:

            print(
                "RANDOM CALL ERROR: REDIS_URL が設定されていません。"
            )

            await self.close(code=1011)
            return

        self.redis = Redis.from_url(
            redis_url,
            decode_responses=True,
        )

        # ==================================================
        # WebSocket ACCEPT
        # ==================================================

        await self.accept()

        print(
            "RANDOM CALL CONNECT:",
            self.user,
            "user_id=",
            self.user.id,
            "gender=",
            self.gender,
            "authenticated=",
            self.user.is_authenticated,
        )

        # ==================================================
        # 接続状態をRedisへ登録
        # ==================================================

        await self.register_connection()

        # ==================================================
        # 自分専用グループ
        # ==================================================

        await self.channel_layer.group_add(
            self.user_group_name,
            self.channel_name,
        )

        # ==================================================
        # 接続完了
        # ==================================================

        await self.send_json({
            "type": "connected",
        })

    # ==================================================
    # プロパティ
    # ==================================================

    @property
    def user_id(self):

        return str(self.user.id)

    @property
    def user_group_name(self):

        return f"random_call_user_{self.user_id}"

    @property
    def connection_key(self):

        return f"{CONNECTED_USER_PREFIX}{self.user_id}"

    # ==================================================
    # Redis 接続状態登録
    # ==================================================

    async def register_connection(self):

        await self.redis.set(
            self.connection_key,
            self.connection_token,
            ex=CONNECTED_TTL,
        )

    # ==================================================
    # Redis 接続状態確認
    # ==================================================

    async def is_user_connected(self, user_id):

        key = f"{CONNECTED_USER_PREFIX}{user_id}"

        token = await self.redis.get(key)

        return token is not None

    # ==================================================
    # 自分の接続状態更新
    #
    # 通話中でも定期的に更新する場合に使用可能
    # ==================================================

    async def refresh_connection(self):

        if not hasattr(self, "redis"):
            return

        current_token = await self.redis.get(
            self.connection_key
        )

        # 自分の接続情報ならTTLを延長
        if current_token == self.connection_token:

            await self.redis.expire(
                self.connection_key,
                CONNECTED_TTL,
            )

    # ==================================================
    # WebSocket 切断
    # ==================================================

    async def disconnect(self, close_code):

        print(
            "RANDOM CALL DISCONNECTED:",
            close_code,
            "user=",
            getattr(self, "user", None),
        )

        # --------------------------------------------------
        # 待機キューから削除
        # --------------------------------------------------

        if hasattr(self, "redis"):

            await self.remove_from_waiting()

        # --------------------------------------------------
        # 通話グループから削除
        # --------------------------------------------------

        if self.call_id:

            await self.channel_layer.group_discard(
                f"random_call_{self.call_id}",
                self.channel_name,
            )

        # --------------------------------------------------
        # 自分のRedis接続情報を削除
        #
        # 別タブが同じユーザーIDで接続している場合、
        # 自分の接続情報を勝手に消さない。
        # --------------------------------------------------

        if hasattr(self, "redis"):

            current_token = await self.redis.get(
                self.connection_key
            )

            if current_token == self.connection_token:

                await self.redis.delete(
                    self.connection_key
                )

            await self.redis.close()

    # ==================================================
    # メッセージ受信
    # ==================================================

    async def receive_json(self, content, **kwargs):

        print(
            "RANDOM CALL RECEIVED:",
            content,
        )

        # 接続TTL更新
        await self.refresh_connection()

        action = content.get("action")

        # --------------------------------------------------
        # 相手を探す
        # --------------------------------------------------

        if action == "find":

            await self.find_partner()

        # --------------------------------------------------
        # キャンセル
        # --------------------------------------------------

        elif action == "cancel":

            await self.cancel_matching()

        # --------------------------------------------------
        # 通話終了
        # --------------------------------------------------

        elif action == "leave":

            await self.leave_call()

        # --------------------------------------------------
        # WebRTC シグナリング
        # --------------------------------------------------

        elif action == "signal":

            await self.forward_signal(content)

    # ==================================================
    # 相手を探す
    # ==================================================

    async def find_partner(self):

        user_id = self.user_id

        # ==================================================
        # すでに通話中
        # ==================================================

        if self.call_id:

            await self.send_json({
                "type": "already_in_call",
                "message": "現在通話中です。",
            })

            return

        # ==================================================
        # すでに待機中
        # ==================================================

        if self.is_waiting:

            await self.send_json({
                "type": "already_waiting",
                "message": "すでに相手を探しています。",
            })

            return

        # ==================================================
        # Redis上ですでに待機していないか確認
        #
        # 複数タブ対策
        # ==================================================

        waiting_queues = [
            WAITING_MALE,
            WAITING_FEMALE,
            WAITING_OTHER,
        ]

        for queue in waiting_queues:

            position = await self.redis.lpos(
                queue,
                user_id,
            )

            if position is not None:

                self.is_waiting = True

                await self.send_json({
                    "type": "already_waiting",
                    "message": "すでに相手を探しています。",
                })

                return

        # ==================================================
        # 自分が探せる相手
        # ==================================================

        if self.gender == "M":

            partner_queues = [
                WAITING_FEMALE,
                WAITING_OTHER,
            ]

        elif self.gender == "F":

            partner_queues = [
                WAITING_MALE,
                WAITING_OTHER,
            ]

        else:

            partner_queues = [
                WAITING_MALE,
                WAITING_FEMALE,
                WAITING_OTHER,
            ]

        # ==================================================
        # 相手を探す
        # ==================================================

        partner_id = None

        while True:

            candidate_id = None

            # --------------------------------------------------
            # 各性別キューから相手を探す
            # --------------------------------------------------

            for queue in partner_queues:

                candidate_id = await self.redis.lpop(
                    queue
                )

                if candidate_id is not None:
                    break

            # --------------------------------------------------
            # 誰もいない
            # --------------------------------------------------

            if candidate_id is None:

                break

            # --------------------------------------------------
            # 自分自身なら無視
            # --------------------------------------------------

            if candidate_id == user_id:

                continue

            # --------------------------------------------------
            # 相手がまだ接続中か確認
            # --------------------------------------------------

            connected = await self.is_user_connected(
                candidate_id
            )

            if not connected:

                print(
                    "RANDOM CALL STALE USER REMOVED:",
                    candidate_id,
                )

                continue

            # --------------------------------------------------
            # 有効な相手
            # --------------------------------------------------

            partner_id = candidate_id

            break

        # ==================================================
        # 相手が見つからない
        # ==================================================

        if partner_id is None:

            waiting_queue = self.get_waiting_queue()

            # --------------------------------------------------
            # 自分を待機キューへ
            # --------------------------------------------------

            await self.redis.rpush(
                waiting_queue,
                user_id,
            )

            self.is_waiting = True

            await self.send_json({
                "type": "waiting",
                "message": "相手を探しています。",
            })

            print(
                "RANDOM CALL WAITING:",
                user_id,
                "gender=",
                self.gender,
            )

            return

        # ==================================================
        # マッチング成立
        # ==================================================

        self.is_waiting = False

        call_id = str(uuid.uuid4())

        self.call_id = call_id

        # --------------------------------------------------
        # 相手専用グループ
        # --------------------------------------------------

        partner_group = (
            f"random_call_user_{partner_id}"
        )

        # --------------------------------------------------
        # 相手へマッチ通知
        # --------------------------------------------------

        await self.channel_layer.group_send(
            partner_group,
            {
                "type": "call_matched",
                "call_id": call_id,
                "partner_id": user_id,
                "is_initiator": False,
            },
        )

        # --------------------------------------------------
        # 自分を通話グループへ
        # --------------------------------------------------

        await self.channel_layer.group_add(
            f"random_call_{call_id}",
            self.channel_name,
        )

        # --------------------------------------------------
        # 自分へ通知
        # --------------------------------------------------

        await self.send_json({
            "type": "matched",
            "call_id": call_id,
            "is_initiator": True,
        })

        print(
            "RANDOM CALL MATCHED:",
            user_id,
            "<->",
            partner_id,
            "CALL:",
            call_id,
        )

    # ==================================================
    # 自分の待機キュー
    # ==================================================

    def get_waiting_queue(self):

        if self.gender == "M":

            return WAITING_MALE

        if self.gender == "F":

            return WAITING_FEMALE

        return WAITING_OTHER

    # ==================================================
    # マッチ成立通知
    # ==================================================

    async def call_matched(self, event):

        # ==================================================
        # すでに別の通話に入っている場合
        # ==================================================

        if self.call_id:

            print(
                "RANDOM CALL MATCH ERROR:",
                self.user_id,
                "already has call:",
                self.call_id,
            )

            return

        # ==================================================
        # 待機状態解除
        # ==================================================

        self.is_waiting = False

        # ==================================================
        # 通話ID
        # ==================================================

        self.call_id = event["call_id"]

        # ==================================================
        # 通話グループ
        # ==================================================

        await self.channel_layer.group_add(
            f"random_call_{self.call_id}",
            self.channel_name,
        )

        # ==================================================
        # マッチ通知
        # ==================================================

        await self.send_json({
            "type": "matched",
            "call_id": self.call_id,
            "is_initiator": False,
        })

        print(
            "RANDOM CALL PARTNER MATCHED:",
            self.user.id,
            "CALL:",
            self.call_id,
        )

    # ==================================================
    # マッチングキャンセル
    # ==================================================

    async def cancel_matching(self):

        # 通話中ならキャンセルではなく無視
        if self.call_id:

            await self.send_json({
                "type": "already_in_call",
                "message": "現在通話中です。",
            })

            return

        await self.remove_from_waiting()

        self.is_waiting = False

        await self.send_json({
            "type": "cancelled",
            "message": "マッチングをキャンセルしました。",
        })

        print(
            "RANDOM CALL CANCEL:",
            self.user.id,
        )

    # ==================================================
    # 待機列から自分を削除
    # ==================================================

    async def remove_from_waiting(self):

        if not hasattr(self, "redis"):
            return

        user_id = self.user_id

        for queue in [
            WAITING_MALE,
            WAITING_FEMALE,
            WAITING_OTHER,
        ]:

            while True:

                removed = await self.redis.lrem(
                    queue,
                    0,
                    user_id,
                )

                if removed == 0:
                    break

        self.is_waiting = False

    # ==================================================
    # 通話終了
    # ==================================================

    async def leave_call(self):

        if not self.call_id:

            await self.send_json({
                "type": "not_in_call",
            })

            return

        call_id = self.call_id

        # ==================================================
        # 相手へ通知
        # ==================================================

        await self.channel_layer.group_send(
            f"random_call_{call_id}",
            {
                "type": "partner_left",
                "user_id": self.user_id,
            },
        )

        # ==================================================
        # 自分を通話グループから削除
        # ==================================================

        await self.channel_layer.group_discard(
            f"random_call_{call_id}",
            self.channel_name,
        )

        self.call_id = None

        await self.send_json({
            "type": "left",
        })

        print(
            "RANDOM CALL LEAVE:",
            self.user_id,
            "CALL:",
            call_id,
        )

    # ==================================================
    # 相手が通話終了
    # ==================================================

    async def partner_left(self, event):

        await self.send_json({
            "type": "partner_left",
        })

        self.call_id = None

        print(
            "RANDOM CALL PARTNER LEFT:",
            self.user_id,
        )

    # ==================================================
    # WebRTC シグナリング
    # ==================================================

    async def forward_signal(self, content):

        if not self.call_id:
            return

        signal_data = content.get("data")

        if signal_data is None:
            return

        await self.channel_layer.group_send(
            f"random_call_{self.call_id}",
            {
                "type": "webrtc_signal",
                "sender_channel": self.channel_name,
                "data": signal_data,
            },
        )

    # ==================================================
    # WebRTC シグナル受信
    # ==================================================

    async def webrtc_signal(self, event):

        # ==================================================
        # 自分が送ったシグナルは自分に返さない
        # ==================================================

        if event["sender_channel"] == self.channel_name:

            return

        await self.send_json({
            "type": "signal",
            "data": event["data"],
        })