from django.forms import ModelForm
from django import forms

from posts.models import Post, Comment


class NewPostForm(ModelForm):
    class Meta:
        model = Post
        fields = ("group", "text", "image")
        labels = {
            "group": "Группа",
            "text": "Текст",
            "image": "Картинка",
        }
        help_texts = {
            "group": "Группа (необязательно)",
            "text": "Текст вашей публикации",
        }


class NewCommentForm(ModelForm):
    text = forms.CharField(widget=forms.Textarea)

    class Meta:
        model = Comment
        fields = ("text",)
        labels = {
            "text": "Текст",
        }
        help_texts = {
            "text": "Текст вашего комментария",
        }
