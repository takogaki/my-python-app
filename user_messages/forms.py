from django import forms

class MessageForm(forms.Form):
    subject = forms.CharField(max_length=100, label="件名")
    message = forms.CharField(widget=forms.Textarea, label="メッセージ")

class ReplyMessageForm(forms.Form):
    reply_message = forms.CharField(widget=forms.Textarea, label="返信メッセージ")