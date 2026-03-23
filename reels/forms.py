from django import forms
from .models import VideoPost

class VideoPostForm(forms.ModelForm):
    class Meta:
        model = VideoPost
        fields = ['video']