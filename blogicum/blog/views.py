from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import PermissionDenied
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView
)
from django.utils import timezone
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy, reverse
from django.core.paginator import Paginator
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.views import PasswordChangeView
from django.contrib.auth.models import User
from django.db.models import Count

from .models import Post, Category, Comment
from .constants import LATEST_POSTS_COUNT
from .forms import PostCreateForm, CommentForm, UserProfileForm


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
        object = self.get_object()
        return object.author == self.request.user



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
    template_name = 'blog/profile.html'
    context_object_name = 'profile'

    def get_object(self):
        return get_object_or_404(User, username=self.kwargs['username'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        posts = Post.objects.filter(
            author=self.object
        ).annotate(comment_count=Count('comments')).order_by('-pub_date')
        paginator = Paginator(posts, 10)
        page_number = self.request.GET.get('page')
        context['page_obj'] = paginator.get_page(page_number)
        return context


class UserProfileEditView(LoginRequiredMixin, UpdateView):
    """Представление для редактирования профиля пользователя."""

    model = User
    form_class = UserProfileForm
    template_name = 'blog/user.html'

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
    login_url = '/login/'
    pk_url_kwarg = 'post_id'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy(
            'blog:profile', kwargs={'username': self.request.user.username}
        )


class PostEditView(OnlyAuthorMixin, UpdateView):
    """Представление для редактирования публикации."""

    model = Post
    form_class = PostCreateForm
    template_name = 'blog/create.html'
    pk_url_kwarg = 'post_id'

    def handle_no_permission(self):
        if not self.test_func():
            return redirect(reverse(
                'blog:post_detail', kwargs={'post_id': self.kwargs['post_id']}
            ))

    def get_success_url(self):
        return reverse_lazy(
            'blog:post_detail', kwargs={'post_id': self.kwargs['post_id']}
        )


class PostDeleteView(LoginRequiredMixin, OnlyAuthorMixin, DeleteView):
    """Представление для удаления публикации."""

    model = Post
    template_name = 'blog/create.html'
    context_object_name = 'post'
    pk_url_kwarg = 'post_id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form = PostCreateForm(instance=self.get_object())
        context['form'] = form
        return context

    def get_success_url(self):
        return reverse_lazy('blog:index')


class CommentCreateView(LoginRequiredMixin, CreateView):
    model = Comment
    form_class = CommentForm

    def get_success_url(self):
        post_id = self.kwargs.get('post_id')
        return reverse('blog:post_detail', kwargs={'post_id': post_id})

    def form_valid(self, form):
        post_id = self.kwargs.get('post_id')
        post = get_object_or_404(Post, id=post_id)
        form.instance.post = post
        form.instance.author = self.request.user
        return super().form_valid(form)



class CommentEditView(CommentMixin, UpdateView):
    """Представление для редактирования комментария."""

    form_class = CommentForm
    success_url = reverse_lazy('blog:index')

    def get_object(self, queryset=None):
        comment_id = self.kwargs.get('comment_id')
        return get_object_or_404(Comment, id=comment_id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['post_id'] = self.kwargs.get('post_id')
        return context


class CommentDeleteView(CommentMixin, DeleteView):
    """Представление для удаления комментария."""

    pk_url_kwarg = 'comment_id'

    def get_success_url(self):
        post_id = self.kwargs.get('post_id')
        return reverse_lazy('blog:post_detail', kwargs={'post_id': post_id})


class PostListView(PublishedPostsMixin, ListView):
    """Отображает главную страницу с последними опубликованными постами."""

    model = Post
    template_name = "blog/index.html"
    context_object_name = "post_list"
    paginate_by = LATEST_POSTS_COUNT

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.annotate(comment_count=Count('comments'))


class PostDetailView(DetailView):
    """Отображает подробную информацию о посте по его ID."""

    model = Post
    template_name = "blog/detail.html"
    context_object_name = "post"
    pk_url_kwarg = 'post_id'

    def get_object(self, queryset=None):
        post_id = self.kwargs.get('post_id')
        post = get_object_or_404(Post, id=post_id)
        if (post.author == self.request.user or (post.is_published
           and post.category.is_published)):
            return post
        raise Http404('Страница не найдена')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = self.get_object()
        context['form'] = CommentForm()
        context['comments'] = post.comments.select_related('author').order_by('pub_date')
        return context


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
