from django.forms import ModelForm

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
    class Meta:
        model = Comment
        fields = "text"
        labels = {
            "text": "Текст",
        }
        help_texts = {
            "text": "Текст вашего комментария",
        }
