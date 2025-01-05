from django import forms

from .models import Post, Category, Location, Comment


class PostCreateForm(forms.ModelForm):
    """Форма для создания нового поста."""

    class Meta:
        model = Post
        fields = ['title', 'text', 'category', 'location', 'pub_date', 'image']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].queryset = Category.objects.filter(
            is_published=True
        )
        self.fields['location'].queryset = Location.objects.filter(
            is_published=True
        )


class CommentForm(forms.ModelForm):
    """Форма для добавления или редактирования комментариев."""

    class Meta:
        model = Comment
        fields = ['text']  # Только текст комментария

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['text'].widget.attrs.update(
            {'class': 'form-control', 'rows': 3}
        )
