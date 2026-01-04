from django import forms
from .models import Message


class MessageForm(forms.Form):
    subject = forms.CharField(max_length=100, label="件名")
    message = forms.CharField(widget=forms.Textarea, label="メッセージ")


# class ReplyMessageForm(forms.Form):
#     reply_message = forms.CharField(widget=forms.Textarea, label="返信メッセージ")


class ReplyMessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ["content"]
        widgets = {
            "content": forms.Textarea(attrs={
                "rows": 5,
                "placeholder": "返信内容を入力してください"
            })
        }