from django.contrib.auth.forms import UserCreationForm
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView
)
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy, reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import PasswordChangeView
from django.contrib.auth.models import User

from .mixins import (
    OnlyAuthorMixin, CommentMixin, PublishedPostsMixin,
    CategoryAvailableMixin, PostMixin
)
from .models import Post, Comment
from .constants import LATEST_POSTS_COUNT
from .forms import PostCreateForm, CommentForm, UserProfileForm
from .utils import get_user, get_user_posts, posts_queryset


class UserRegistrationView(CreateView):
    """Отображает форму для регистрации пользователей."""

    template_name = 'registration/registration_form.html'
    form_class = UserCreationForm
    success_url = reverse_lazy('login')


class UserProfileView(ListView):
    """Отображает профиль пользователя."""

    model = Post
    template_name = 'blog/profile.html'
    context_object_name = 'post_list'
    paginate_by = LATEST_POSTS_COUNT

    def get_queryset(self):
        profile = get_user(self.kwargs.get('username'))
        return get_user_posts(profile.posts)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = get_object_or_404(
            User,
            username=self.kwargs['username']
        )
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
    pk_url_kwarg = 'post_id'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy(
            'blog:profile', kwargs={'username': self.request.user.username}
        )


class PostEditView(PostMixin, OnlyAuthorMixin, UpdateView):
    """Представление для редактирования публикации."""

    form_class = PostCreateForm

    def handle_no_permission(self):
        if not self.test_func():
            return redirect(reverse(
                'blog:post_detail', kwargs={'post_id': self.kwargs['post_id']}
            ))


class PostDeleteView(PostMixin, OnlyAuthorMixin, DeleteView):
    """Представление для удаления публикации."""

    context_object_name = 'post'

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


class CommentDeleteView(CommentMixin, DeleteView):
    """Представление для удаления комментария."""

    pk_url_kwarg = 'comment_id'

    def get_success_url(self):
        post_id = self.kwargs.get('post_id')
        return reverse_lazy('blog:post_detail', kwargs={'post_id': post_id})


class PostListView(PublishedPostsMixin, ListView):
    """Отображает главную страницу с последними опубликованными постами."""

    model = Post
    template_name = 'blog/index.html'
    context_object_name = 'post_list'
    paginate_by = LATEST_POSTS_COUNT

    def get_queryset(self):
        return posts_queryset(Post.objects)


class PostDetailView(DetailView):
    """Отображает подробную информацию о посте по его ID."""

    model = Post
    template_name = 'blog/detail.html'
    context_object_name = 'post'
    pk_url_kwarg = 'post_id'

    def get_object(self, queryset=None):
        post_id = self.kwargs.get('post_id')
        post = get_object_or_404(Post, id=post_id)
        if (
            post.author == self.request.user
            or (post.is_published and post.category.is_published)
        ):
            return post
        raise Http404('Страница не найдена')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = self.get_object()
        context['form'] = CommentForm()
        context['comments'] = (post.comments.select_related('author')
                               .order_by('pub_date'))
        return context


class CategoryPostListView(CategoryAvailableMixin, ListView):
    """Отображает все посты, относящиеся к заданной категории."""

    model = Post
    template_name = 'blog/category.html'
    context_object_name = 'post_list'
    paginate_by = LATEST_POSTS_COUNT

    def get_queryset(self):
        return posts_queryset(self.get_category().posts)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.get_category()
        return context
