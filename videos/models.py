from django.conf import settings
from django.db import models
from cloudinary.models import CloudinaryField


# =========================
# 🎬 投稿（動画・画像統合）
# =========================
class PostVideo(models.Model):

    MEDIA_TYPE_CHOICES = [
        ("video", "動画"),
        ("image", "画像"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="post_videos"
    )

    media_type = models.CharField(
        max_length=10,
        choices=MEDIA_TYPE_CHOICES
    )

    # 🔥 分離
    image = CloudinaryField(
        "image",
        blank=True,
        null=True
    )

    video = models.FileField(
        upload_to="videos/",
        blank=True,
        null=True
    )

    caption = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    views_count = models.PositiveIntegerField(default=0)
    likes_count = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["-created_at"]),
            models.Index(fields=["user"]),
        ]

    def __str__(self):
        return f"{self.user} - {self.id}"

    def like_count(self):
        return self.likes_count  # 🔥 DBカラム使う

    def comment_count(self):
        return self.comments.count()


# =========================
# ❤️ いいね（完全版）
# =========================
class PostVideoLike(models.Model):

    # 🔐 ログインユーザー
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="liked_videos"
    )

    # 👤 未ログイン識別子
    guest_id = models.CharField(
        max_length=64,
        null=True,
        blank=True
    )

    post = models.ForeignKey(
        PostVideo,
        on_delete=models.CASCADE,
        related_name="likes"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["user"]),
            models.Index(fields=["guest_id"]),
            models.Index(fields=["post"]),
        ]

        # 🔥 制約（どちらか一方で一意）
        constraints = [
            models.UniqueConstraint(
                fields=["user", "post"],
                name="unique_user_like",
                condition=models.Q(user__isnull=False)
            ),
            models.UniqueConstraint(
                fields=["guest_id", "post"],
                name="unique_guest_like",
                condition=models.Q(guest_id__isnull=False)
            ),
        ]

    def __str__(self):
        return f"{self.user or self.guest_id} ❤️ {self.post.id}"


# =========================
# 💬 コメント
# =========================
class PostVideoComment(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    post = models.ForeignKey(
        PostVideo,
        on_delete=models.CASCADE,
        related_name="comments"
    )

    text = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["post"]),
        ]

    def __str__(self):
        return f"{self.user} - {self.post.id}"


# =========================
# 🔖 保存
# =========================
class PostVideoSave(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="saved_post_videos"
    )

    post = models.ForeignKey(
        PostVideo,
        on_delete=models.CASCADE,
        related_name="saved_by"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "post")

    def __str__(self):
        return f"{self.user} 🔖 {self.post.id}"
    
# =========================
# 🤝 募集
# =========================
class Recruit(models.Model):

    CATEGORY_CHOICES = [
        ("drink", "飲み"),
        ("food", "ご飯"),
        ("karaoke", "カラオケ"),
        ("cafe", "カフェ"),
        ("sports", "スポーツ"),
        ("game", "ゲーム"),
        ("drive", "ドライブ"),
        ("study", "勉強"),
        ("other", "その他"),
    ]

    STATUS_CHOICES = [
        ("open", "募集中"),
        ("full", "満員"),
        ("closed", "終了"),
        ("cancel", "中止"),
    ]

    GENDER_CHOICES = [
        ("all", "誰でも"),
        ("male", "男性のみ"),
        ("female", "女性のみ"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="recruits"
    )

    # 募集カテゴリ
    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES
    )

    # タイトル
    title = models.CharField(
        max_length=100
    )

    # 詳細
    description = models.TextField(
        blank=True
    )

    # 開催場所
    place = models.CharField(
        max_length=100,
        blank=True
    )

    # 都道府県
    prefecture = models.CharField(
        max_length=30,
        blank=True
    )

    # 開始時間
    start_time = models.DateTimeField(
        null=True,
        blank=True
    )

    # 終了時間
    end_time = models.DateTimeField(
        null=True,
        blank=True
    )

    # 募集終了期限
    expires_at = models.DateTimeField(
        null=True,
        blank=True
    )

    # 最大人数
    max_people = models.PositiveIntegerField(
        default=2
    )

    # 対象性別
    target_gender = models.CharField(
        max_length=20,
        choices=GENDER_CHOICES,
        default="all"
    )

    # 業界（例：建設業、看護師など）
    industry = models.CharField(
        max_length=50,
        blank=True
    )

    # 募集状態
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="open"
    )

    # 公開中か
    is_active = models.BooleanField(
        default=True
    )

    # 中止時に応募者を保持したか
    cancel_keep_participants = models.BooleanField(
        default=False
    )

    # 作成日時・更新日時
    created_at = models.DateTimeField(
        auto_now_add=True
    )

    # 更新日時
    updated_at = models.DateTimeField(
        auto_now=True
    )

    # 画像（任意）
    image = models.ImageField(
        upload_to="recruits/",
        blank=True,
        null=True
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user} - {self.title}"


    @property
    def approved_count(self):
        return self.participants.filter(
            status="approved"
        ).count()


    @property
    def pending_count(self):
        return self.participants.filter(
            status="pending"
        ).count()


    @property
    def remaining_count(self):
        return max(
            self.max_people - self.approved_count,
            0
        )
            

# =========================
# 🙋 募集参加者
# =========================
class RecruitParticipant(models.Model):

    STATUS_CHOICES = [
        ("pending", "承認待ち"),
        ("approved", "参加確定"),
        ("rejected", "拒否"),
        ("cancelled", "キャンセル"),
    ]

    recruit = models.ForeignKey(
        Recruit,
        on_delete=models.CASCADE,
        related_name="participants"
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="joined_recruits"
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending"
    )

    message = models.CharField(
        max_length=200,
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = ["created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["recruit", "user"],
                name="unique_recruit_participant"
            )
        ]

    def __str__(self):
        return f"{self.user} → {self.recruit.title} ({self.status})"


# =========================
# 💬 募集チャットルーム
# =========================
class RecruitChatRoom(models.Model):

    recruit = models.OneToOneField(
        Recruit,
        on_delete=models.CASCADE,
        related_name="chat_room"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return f"Chat: {self.recruit.title}"


# =========================
# 💬 募集チャットメッセージ
# =========================
class RecruitChatMessage(models.Model):

    room = models.ForeignKey(
        RecruitChatRoom,
        on_delete=models.CASCADE,
        related_name="messages"
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="recruit_chat_messages"
    )

    text = models.TextField()

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = ["created_at"]
        indexes = [
            models.Index(
                fields=["room", "created_at"]
            ),
        ]

    def __str__(self):
        return f"{self.user.username}: {self.text[:30]}"
    
class RecruitChatRead(models.Model):

    room = models.ForeignKey(
        RecruitChatRoom,
        on_delete=models.CASCADE,
        related_name="read_states",
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="recruit_chat_read_states",
    )

    last_read_message = models.ForeignKey(
        RecruitChatMessage,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="+",
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["room", "user"],
                name="unique_recruit_chat_read_state",
            )
        ]

    def __str__(self):
        return (
            f"{self.user.username} - "
            f"{self.room.recruit.title}"
        )