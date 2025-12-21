from django import forms
from .models import Post, Comment
from faker import Faker

fake = Faker()

# =======================
# Post の投稿フォーム
# =======================
class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ["title", "body", "image", "youtube_url"]   # カイト様の元の通り
        widgets = {
            "name": forms.TextInput(attrs={
                "placeholder": "匿名可",
            }),
        }

# =======================
# コメントフォーム
# =======================
class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ["body", "image", "youtube_url"]   # コメントに必要な2つだけ
        widgets = {
            "name": forms.TextInput(attrs={
                "placeholder": "匿名可",
            }),
        }

        name = forms.CharField(required=False)

    def __init__(self, *args, **kwargs):
        self.parent = kwargs.pop('parent', None)
        super().__init__(*args, **kwargs)

# 🔽 ここが超重要
        self.fields["name"].required = False

        if self.parent:
            # 返信の場合、placeholder を変更
            self.fields['body'].widget.attrs['placeholder'] = (
                f"{self.parent.name} さんに返信する"
            )
