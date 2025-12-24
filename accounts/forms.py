# accounts/forms.py
from django import forms
from .models import CustomUser
from django.contrib.auth.forms import UserCreationForm
from datetime import datetime

class CustomUserCreationForm(UserCreationForm):

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