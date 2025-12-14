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
        fields = ["name", "title", "body"]   # カイト様の元の通り


# =======================
# コメントフォーム
# =======================
class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ["name", "body"]   # コメントに必要な2つだけ

    def __init__(self, *args, **kwargs):
        self.parent = kwargs.pop('parent', None)
        super().__init__(*args, **kwargs)

        if self.parent:
            # 返信の場合、placeholder を変更
            self.fields['body'].widget.attrs['placeholder'] = (
                f"{self.parent.name} さんに返信する"
            )
