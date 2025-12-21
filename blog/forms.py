from django import forms
from .models import Post, Comment
from faker import Faker

fake = Faker()

# =======================
# Post の投稿フォーム
# =======================
class PostForm(forms.ModelForm):
    name = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                "placeholder": "匿名可",
            }
        ),
        label="名前",
    )

    class Meta:
        model = Post
        fields = ["name", "title", "body", "image", "youtube_url"]
        widgets = {
            "title": forms.TextInput(attrs={
                "placeholder": "タイトル",
            }),
            "body": forms.Textarea(attrs={
                "placeholder": "本文を入力してください",
                "rows": 6,
            }),
        }

    def clean_name(self):
        """
        名前が未入力の場合は None を返す
        （Model.save() 側で faker による自動補完が動く）
        """
        name = self.cleaned_data.get("name")
        return name or None


# =======================
# コメントフォーム
# =======================
class CommentForm(forms.ModelForm):
    name = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                "placeholder": "匿名可",
            }
        ),
        label="名前",
    )

    class Meta:
        model = Comment
        fields = ["name", "body", "image", "youtube_url"]
        widgets = {
            "body": forms.Textarea(attrs={
                "placeholder": "コメントを書く",
                "rows": 3,
            }),
        }

    def __init__(self, *args, **kwargs):
        self.parent = kwargs.pop("parent", None)
        super().__init__(*args, **kwargs)

        # 返信時のプレースホルダー変更
        if self.parent:
            parent_name = self.parent.name or "匿名"
            self.fields["body"].widget.attrs["placeholder"] = (
                f"{parent_name} さんに返信する"
            )

    def clean_name(self):
        """
        未入力なら None（Model 側で処理）
        """
        name = self.cleaned_data.get("name")
        return name or None