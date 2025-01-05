from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView
)
from django.utils import timezone
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.core.paginator import Paginator
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.views import PasswordChangeView

from .models import Post, Category, Comment
from .constants import LATEST_POSTS_COUNT
from .forms import PostCreateForm, CommentForm


class PublishedPostsMixin:
    """Mixin для фильтрации опубликованных постов."""

    def get_queryset(self):
        now = timezone.now()
        return (
            Post.objects.filter(
                pub_date__lte=now,
                is_published=True,
                category__is_published=True
            ).order_by("-pub_date")[:LATEST_POSTS_COUNT]
        )


class PostAvailableMixin:
    """Mixin для проверки доступности поста."""

    def get_object(self, queryset=None):
        post = super().get_object(queryset)
        if (
            post.pub_date > timezone.now() or
            not post.is_published or
            not post.category.is_published
        ):
            raise Http404("Публикация недоступна.")
        return post


class CategoryAvailableMixin:
    """Mixin для проверки доступности категории."""

    def get_category(self):
        category_slug = self.kwargs["category_slug"]
        category = get_object_or_404(Category, slug=category_slug)

        if not category.is_published:
            raise Http404("Категория скрыта.")

        return category


class UserRegistrationView(CreateView):
    """Отображает форму для регистрации пользователей."""

    template_name = 'registration/registration_form.html'
    form_class = UserCreationForm
    success_url = reverse_lazy('login')


class UserProfileView(DetailView):
    """Отображает профиль пользователя."""

    model = User
    template_name = 'profile.html'
    context_object_name = 'profile'

    def get_object(self):
        return get_object_or_404(User, username=self.kwargs['username'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        posts = Post.objects.filter(
            author=self.object, is_published=True
        ).order_by('-pub_date')
        paginator = Paginator(posts, 10)
        page_number = self.request.GET.get('page')
        context['page_obj'] = paginator.get_page(page_number)
        return context


class UserProfileEditView(LoginRequiredMixin, UpdateView):
    """Представление для редактирования профиля пользователя."""

    model = User
    form_class = UserChangeForm
    template_name = 'user.html'

    def get_object(self, queryset=None):
        return self.request.user

    def get_success_url(self):
        return reverse_lazy(
            'blog:profile', kwargs={'username': self.request.user.username}
        )


class UserPasswordChangeView(PasswordChangeView):
    """Представление для изменения пароля пользователя."""

    template_name = 'password_change_form.html'
    success_url = reverse_lazy('login')


class PostCreateView(LoginRequiredMixin, CreateView):
    """Представление для создания новой публикации."""

    model = Post
    form_class = PostCreateForm
    template_name = 'blog/create.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        if form.instance.pub_date > timezone.now():
            form.instance.is_published = False
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy(
            'blog:profile', kwargs={'username': self.request.user.username}
        )


class PostEditView(LoginRequiredMixin, UpdateView):
    """Представление для редактирования публикации."""

    model = Post
    form_class = PostCreateForm
    template_name = 'blog/create.html'

    def form_valid(self, form):
        if form.instance.pub_date > timezone.now():
            form.instance.is_published = False
        return super().form_valid(form)

    def get_object(self, queryset=None):
        post = super().get_object(queryset)
        if post.author != self.request.user:
            raise Http404("У вас нет прав для редактирования этого поста.")
        return post

    def get_success_url(self):
        return reverse_lazy('blog:post_detail', kwargs={'id': self.object.id})


class PostDeleteView(LoginRequiredMixin, DeleteView):
    """Представление для удаления публикации."""

    model = Post
    template_name = 'blog/post_confirm_delete.html'
    context_object_name = 'post'

    def get_object(self, queryset=None):
        post = super().get_object(queryset)
        if post.author != self.request.user:
            raise Http404("У вас нет прав для удаления этого поста.")
        return post

    def get_success_url(self):
        return reverse_lazy('blog:index')


class CommentCreateView(LoginRequiredMixin, CreateView):
    """Представление для добавления комментария к посту."""

    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment_form.html'

    def form_valid(self, form):
        post = Post.objects.get(id=self.kwargs['post_id'])
        if not post.is_published or post.pub_date > timezone.now():
            raise Http404("Публикация недоступна.")
        form.instance.author = self.request.user
        form.instance.post = post
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy(
            'blog:post_detail', kwargs={'id': self.kwargs['post_id']}
        )


class CommentEditView(LoginRequiredMixin, UpdateView):
    """Представление для редактирования комментария."""

    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment_form.html'

    def get_object(self, queryset=None):
        comment = super().get_object(queryset)
        if comment.author != self.request.user:
            raise Http404("У вас нет прав для редактирования этого комментария.")
        return comment

    def get_success_url(self):
        return reverse_lazy(
            'blog:post_detail', kwargs={'id': self.object.post.id}
        )


class CommentDeleteView(LoginRequiredMixin, DeleteView):
    """Представление для удаления комментария."""

    model = Comment
    template_name = 'blog/comment_confirm_delete.html'
    context_object_name = 'comment'

    def get_object(self, queryset=None):
        comment = super().get_object(queryset)
        if comment.author != self.request.user:
            raise Http404("У вас нет прав для удаления этого комментария.")
        return comment

    def get_success_url(self):
        return reverse_lazy(
            'blog:post_detail', kwargs={'id': self.object.post.id}
        )


class PostListView(PublishedPostsMixin, ListView):
    """Отображает главную страницу с последними опубликованными постами."""

    model = Post
    template_name = "blog/index.html"
    context_object_name = "post_list"
    paginate_by = LATEST_POSTS_COUNT


class PostDetailView(PostAvailableMixin, DetailView):
    """Отображает подробную информацию о посте по его ID."""

    model = Post
    template_name = "blog/detail.html"
    context_object_name = "post"


class CategoryPostListView(CategoryAvailableMixin, ListView):
    """Отображает все посты, относящиеся к заданной категории."""

    model = Post
    template_name = "blog/category.html"
    context_object_name = "post_list"
    paginate_by = LATEST_POSTS_COUNT

    def get_queryset(self):
        category = self.get_category()
        return Post.objects.filter(
            category=category,
            pub_date__lte=timezone.now(),
            is_published=True
        ).order_by("-pub_date")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["category"] = self.get_category()
        return context
