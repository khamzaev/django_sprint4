from django.http import Http404
from django.utils import timezone
from django.shortcuts import render, get_object_or_404

from .models import Post, Category
from .constants import LATEST_POSTS_COUNT


def index(request):
    """Отображает главную страницу с последними 5 опубликованными постами."""
    now = timezone.now()
    posts = Post.objects.filter(
        pub_date__lte=now,
        is_published=True,
        category__is_published=True
    ).order_by("-pub_date")[:LATEST_POSTS_COUNT]

    return render(
        request,
        "blog/index.html",
        {"post_list": posts}
    )


def post_detail(request, id):
    """Отображает подробную информацию о посте по его ID."""
    post = get_object_or_404(Post, id=id)

    if (
            post.pub_date > timezone.now()
            or not post.is_published
            or not post.category.is_published
    ):
        raise Http404("Публикация недоступна.")

    return render(
        request,
        "blog/detail.html",
        {"post": post}
    )


def category_posts(request, category_slug):
    """
    Отображает все посты, относящиеся к заданной категории.
    Если категория не опубликована — возвращаем ошибку 404.
    """
    category = get_object_or_404(Category, slug=category_slug)

    if not category.is_published:
        raise Http404("Категория скрыта.")

    posts = category.posts.filter(
        category=category,
        pub_date__lte=timezone.now(),
        is_published=True
    ).order_by("-pub_date")

    return render(
        request,
        "blog/category.html",
        {"post_list": posts, "category": category})
