from django import forms
from django.contrib.auth.models import User

from .models import Post, Comment


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email']


class PostCreateForm(forms.ModelForm):
    """Форма для создания нового поста."""

    class Meta:
        model = Post
        exclude = ['author', 'users_like']
        widgets = {
            'pub_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }


class CommentForm(forms.ModelForm):
    """Форма для добавления или редактирования комментариев."""

    class Meta:
        model = Comment
        fields = ['text']  # Только текст комментария
