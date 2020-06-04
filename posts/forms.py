from django import forms
from django.forms import ModelForm

from .models import Post, Comment


class PostForm(ModelForm):
    class Meta:
        model = Post
        fields = ("text", "group", "image")
        labels = {"text": "Текст записи", "group": "Название группы",
                  "image": "Картинка", }


class CommentForm(ModelForm):
    text = forms.CharField(required=True, widget=forms.Textarea)

    class Meta:
        model = Comment
        fields = ("text", )
        labels = {"author": "Автор комментария", "text": "Текст комментария", }
