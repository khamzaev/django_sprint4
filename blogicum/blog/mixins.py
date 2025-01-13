from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import DeleteView

from .forms import CommentForm
from .models import Comment, Post, Category


class CommentMixin(LoginRequiredMixin):
    """Общий миксин для работы с комментариями: редактирование и удаление."""

    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'comment_id'

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.author != request.user:
            raise PermissionDenied(
                'Вы не авторизованы для выполнения этого действия.'
            )
        return super().dispatch(request, *args, **kwargs)

    def get_object(self, queryset=None):
        return get_object_or_404(
            Comment,
            id=self.kwargs.get(self.pk_url_kwarg),
            post_id=self.kwargs.get('post_id')
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if isinstance(self, DeleteView):
            context['form'] = None
        else:
            context['form'] = self.form_class(instance=self.object)
        context['post_id'] = self.kwargs.get('post_id')
        return context

    def post(self, request, *args, **kwargs):
        if isinstance(self, DeleteView):
            self.success_url = self.get_success_url()
            self.get_object().delete()
            return redirect(self.success_url)
        return super().post(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy(
            'blog:post_detail',
            kwargs={'post_id': self.kwargs.get('post_id')}
        )


class OnlyAuthorMixin(UserPassesTestMixin):

    def test_func(self):
        obj = self.get_object()
        return obj.author == self.request.user


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
