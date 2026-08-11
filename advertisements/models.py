from django.db import models


class Advertisement(models.Model):

    # =========================
    # 📢 プログラム名
    # =========================
    name = models.CharField(
        max_length=200,
        verbose_name="プログラム名"
    )

    # =========================
    # 🧩 A8広告素材HTML
    # =========================
    html = models.TextField(
        blank=True,
        default="",
        verbose_name="A8広告素材HTML",
        help_text="A8.netの「素材をコピー」で取得したHTMLをそのまま貼り付けてください。"
    )

    # =========================
    # 📍 掲載場所
    # =========================
    PLACEMENT_CHOICES = [
        ("feed", "Feed"),
        ("frontpage", "Frontpage"),
        ("user_list", "User List"),
        ("both", "全て"),
    ]

    placement = models.CharField(
        max_length=50,
        choices=PLACEMENT_CHOICES,
        default="feed",
        verbose_name="掲載場所"
    )

    # =========================
    # ON / OFF
    # =========================
    is_active = models.BooleanField(
        default=True,
        verbose_name="有効"
    )

    # =========================
    # 作成日時
    # =========================
    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.name