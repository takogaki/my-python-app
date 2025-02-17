#diary
from django.forms import ModelForm
from .models import Page

#diary
class PageForm(ModelForm):
    class Meta:
        model  = Page
        fields = ["title", "body", "page_date", "picture", 'is_public']