from django import forms
from .models import CustomUser
from django.contrib.auth.forms import UserCreationForm
from datetime import datetime

class CustomUserCreationForm(UserCreationForm):
    # birth_date を8桁の形式で入力させるためのCharFieldに変更
    birth_date_input = forms.CharField(
        max_length=8,
        label="任意)生年月日（8桁で入力: 例 19901114）",
        required=True,
    )

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ['username', 'password1', 'password2', 'name', 'birth_date_input', 'gender', 'address', 'emergency_contact_phone', 'email']

    def clean_birth_date_input(self):
        birth_date_input = self.cleaned_data['birth_date_input']
        
        # 8桁かどうかのチェック
        if not birth_date_input.isdigit() or len(birth_date_input) != 8:
            raise forms.ValidationError("生年月日は8桁の数字で入力してください。（例: 19901114）")
        
        try:
            # 日付に変換
            birth_date = datetime.strptime(birth_date_input, '%Y%m%d').date()
        except ValueError:
            raise forms.ValidationError("有効な日付を入力してください。")

        # 未来の日付は無効
        if birth_date > datetime.now().date():
            raise forms.ValidationError("未来の日付は無効です。")
        
        return birth_date

    def save(self, commit=True):
        user = super().save(commit=False)
        # 変換した日付を birth_date に保存
        user.birth_date = self.cleaned_data['birth_date_input']
        if commit:
            user.save()
        return user