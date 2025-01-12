from django.urls import reverse_lazy
from django.utils import timezone
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.shortcuts import get_object_or_404

from .constants import LATEST_POSTS_COUNT
from .forms import CommentForm
from .models import Comment, Post, Category


class CommentMixin(LoginRequiredMixin):
    model = Comment
    template_name = 'blog/comment.html'

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.author != request.user:
            raise PermissionDenied(
                'Вы не авторизованы для удаления этого комментария.'
            )
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if '/delete_comment/' in self.request.path:
            context['form'] = None
        else:
            context['form'] = CommentForm(instance=self.object)
        context['post_id'] = self.kwargs.get('post_id')
        return context


class OnlyAuthorMixin(UserPassesTestMixin):

    def test_func(self):
        obj = self.get_object()
        return obj.author == self.request.user


class PublishedPostsMixin:
    """Mixin для фильтрации опубликованных постов."""

    def get_queryset(self):
        now = timezone.now()
        return (
            Post.objects.filter(
                pub_date__lte=now,
                is_published=True,
                category__is_published=True
            ).order_by('-pub_date')[:LATEST_POSTS_COUNT]
        )


class CategoryAvailableMixin:
    """Mixin для проверки доступности категории."""

    def get_category(self):
        category_slug = self.kwargs['category_slug']
        category = get_object_or_404(Category, slug=category_slug)

        if not category.is_published:
            raise Http404('Категория скрыта.')

        return category


class PostMixin(LoginRequiredMixin):
    """Миксин для общего функционала редактирования и удаления публикации."""

    model = Post
    pk_url_kwarg = 'post_id'
    template_name = 'blog/create.html'

    def get_object(self, queryset=None):
        return get_object_or_404(self.model, id=self.kwargs[self.pk_url_kwarg])

    def get_success_url(self):
        return reverse_lazy(
            'blog:post_detail', kwargs={'post_id': self.kwargs['post_id']}
        )
