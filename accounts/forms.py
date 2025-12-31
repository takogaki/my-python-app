# accounts/forms.py
from django import forms
from .models import CustomUser
from django.contrib.auth.forms import UserCreationForm
from datetime import datetime
from .models import Profile
from django.contrib.auth import get_user_model
import re

from django.core.exceptions import ValidationError

def validate_username_ascii(value):
    """
    英数字・アンダースコアのみ許可
    """
    if not re.match(r'^[a-zA-Z0-9_]+$', value):
        raise ValidationError(
            "ユーザー名は英数字とアンダースコアのみ使用できます。"
        )

class CustomUserCreationForm(UserCreationForm):

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
        ]

    def clean_birth_date_input(self):
        value = self.cleaned_data["birth_date_input"]

        if not value.isdigit() or len(value) != 8:
            raise forms.ValidationError("生年月日は数字8桁で入力してください（例：19901114）")

        try:
            birth_date = datetime.strptime(value, "%Y%m%d").date()
        except ValueError:
            raise forms.ValidationError("存在しない日付です")

        if birth_date > datetime.now().date():
            raise forms.ValidationError("未来の日付は指定できません")

        return birth_date

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_active = False  # ← 本番対応ポイント
        if commit:
            user.save()
        return user
    

# ユーザーネーム編集フォーム
User = get_user_model()

class ProfileForm(forms.ModelForm):
    username = forms.CharField(
        required=False,
        label="ユーザー名",
        validators=[validate_username_ascii],
    )

    class Meta:
        model = User
        fields = ["username", "profile_image"]

    def clean_username(self):
        username = self.cleaned_data.get("username")

        # 空なら変更しない
        if not username:
            return self.instance.username

        # 自分以外で重複チェック
        if User.objects.exclude(pk=self.instance.pk).filter(username=username).exists():
            raise ValidationError("このユーザー名は既に使用されています。")

        return username

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
        return user