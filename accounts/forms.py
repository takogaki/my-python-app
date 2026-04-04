from django import forms
from .models import CustomUser, KYCSubmission
from django.contrib.auth.forms import UserCreationForm
from datetime import datetime
from .models import Profile
from django.contrib.auth import get_user_model
import re
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.utils import timezone

User = get_user_model()

# =========================
# 🔥 共通バリデーション
# =========================
def validate_profile_image(image):
    if not image:
        return image

    allowed_types = [
        "image/png",
        "image/jpeg",
        "image/webp",
    ]

    if image.content_type not in allowed_types:
        raise ValidationError("画像形式は PNG / JPG / WEBP のみ対応しています。")

    max_size = 2 * 1024 * 1024  # 2MB
    if image.size > max_size:
        raise ValidationError("画像サイズは2MB以内にしてください。")

    return image


def validate_kyc_image(image):
    if not image:
        raise ValidationError("画像をアップロードしてください。")

    allowed_types = [
        "image/png",
        "image/jpeg",
        "image/webp",
    ]

    if image.content_type not in allowed_types:
        raise ValidationError("対応形式は PNG / JPG / WEBP のみです。")

    max_size = 5 * 1024 * 1024  # 5MB
    if image.size > max_size:
        raise ValidationError("画像サイズは5MB以内にしてください。")

    return image


def validate_username_ascii(value):
    if not re.match(r'^[a-zA-Z0-9_]+$', value):
        raise ValidationError("ユーザー名は英数字とアンダースコアのみ使用できます。")


# =========================
# 🔥 ユーザー登録
# =========================
class CustomUserCreationForm(UserCreationForm):

    agree = forms.BooleanField(
        required=True,
        label="利用規約に同意する"
    )

    def clean(self):
        cleaned_data = super().clean()

        if not cleaned_data.get("agree"):
            raise ValidationError("利用規約に同意してください")

        return cleaned_data

    username = forms.CharField(
        label="ユーザー名",
        validators=[validate_username_ascii],
    )

    birth_date_input = forms.CharField(
        max_length=8,
        label="生年月日（8桁の数字）",
        required=True,
        widget=forms.TextInput(attrs={
            "placeholder": "例：19901114",
            "inputmode": "numeric",
            "pattern": "[0-9]{8}",
        })
    )

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = [
            "username",
            "password1",
            "password2",
            "gender",
            "email",
            "birth_date_input",
            "agree",
        ]

    def clean_username(self):
        username = self.cleaned_data["username"]
        if User.objects.filter(username=username).exists():
            raise ValidationError("このユーザー名はすでに使用されています。")
        return username

    def clean_birth_date_input(self):
        value = self.cleaned_data["birth_date_input"]

        if not value.isdigit() or len(value) != 8:
            raise ValidationError("生年月日は数字8桁で入力してください（例：19901114）")

        try:
            birth_date = datetime.strptime(value, "%Y%m%d").date()
        except ValueError:
            raise ValidationError("存在しない日付です")

        if birth_date > datetime.now().date():
            raise ValidationError("未来の日付は指定できません")

        return birth_date

    def save(self, commit=True):
        user = super().save(commit=False)
        user.birth_date = self.cleaned_data["birth_date_input"]
        user.is_active = False

        user.agreed_terms_at = timezone.now()

        if commit:
            user.save()
        return user


# =========================
# 🔥 プロフィール編集
# =========================
class ProfileForm(forms.ModelForm):
    username = forms.CharField(
        required=False,
        label="ユーザー名",
        validators=[validate_username_ascii],
    )

    profile_image = forms.ImageField(
        required=False,
        widget=forms.ClearableFileInput(attrs={
            "accept": "image/png,image/jpeg,image/webp"
        })
    )

    class Meta:
        model = User
        fields = ["username", "profile_image"]

    def clean_profile_image(self):
        image = self.cleaned_data.get("profile_image")
        return validate_profile_image(image)

    def clean_username(self):
        username = self.cleaned_data.get("username")

        if not username:
            return self.instance.username

        if User.objects.exclude(pk=self.instance.pk).filter(username=username).exists():
            raise ValidationError("このユーザー名は既に使用されています。")

        return username

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
        return user


# =========================
# 🔥 初回プロフィール画像
# =========================
class ActivateProfileImageForm(forms.ModelForm):
    profile_image = forms.ImageField(
        required=False,
        widget=forms.ClearableFileInput(attrs={
            "accept": "image/png,image/jpeg,image/webp"
        })
    )

    class Meta:
        model = User
        fields = ["profile_image"]

    def clean_profile_image(self):
        image = self.cleaned_data.get("profile_image")
        return validate_profile_image(image)


# =========================
# 🔥 KYCフォーム（超重要）
# =========================
class KYCForm(forms.ModelForm):
    class Meta:
        model = KYCSubmission
        fields = ["id_image", "selfie_image"]

    def clean_id_image(self):
        image = self.cleaned_data.get("id_image")
        return validate_kyc_image(image)

    def clean_selfie_image(self):
        image = self.cleaned_data.get("selfie_image")
        return validate_kyc_image(image)

    def clean(self):
        cleaned_data = super().clean()

        user = None

        # 🔥 ここが最重要（例外を握り潰す）
        try:
            user = self.instance.user
        except ObjectDoesNotExist:
            user = None

        # 🔥 requestから取得（これが本命）
        if not user and hasattr(self, "request"):
            user = self.request.user

        if not user:
            return cleaned_data

        if user.verification_attempts >= 3:
            raise ValidationError(
                "認証の試行回数が上限に達しました。サポートにお問い合わせください。"
            )

        return cleaned_data