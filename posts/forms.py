from django.forms import ModelForm

from posts.models import Post


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
