from django import forms
from django.forms import ModelForm
from .models import Page


class PageForm(ModelForm):

    class Meta:
        model = Page
        fields = ["title", "body", "page_date", "picture", "is_public"]

        widgets = {
            "title": forms.TextInput(attrs={
                "class": "form-input"
            }),

            "body": forms.Textarea(attrs={
                "class": "form-textarea"
            }),

            "page_date": forms.DateInput(attrs={
                "type": "date",
                "class": "form-input"
            }),

            "picture": forms.ClearableFileInput(attrs={
                "class": "form-file"
            }),

            "is_public": forms.CheckboxInput(attrs={
                "class": "form-check-input"
            })
        }