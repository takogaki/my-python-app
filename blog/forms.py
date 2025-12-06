#blog
from django import forms
from .models import Post
from django.forms import ModelForm

#comment
from .models import Comment
from faker import Faker

#blog
class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ["name", "title", "body"]

#comment
fake = Faker()

class CommentForm(forms.ModelForm):
    from django import forms
from .models import Post

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ["title", "content"]  # モデルに合わせて調整

    class Meta:
        model = Comment
        fields = ["name", "body"]  # 自分の名前とコメント本文のみをフォームに表示

    def __init__(self, *args, **kwargs):
        self.parent = kwargs.pop('parent', None)  # 親コメントを受け取る
        super().__init__(*args, **kwargs)
        if self.parent:
            # プレースホルダーに宛名情報を表示
            self.fields['body'].widget.attrs['placeholder'] = f"{self.parent.name}さんに返信する"