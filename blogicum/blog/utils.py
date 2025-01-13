from django.db.models.functions import Now
from django.shortcuts import get_object_or_404
from django.db.models import Count

from .models import User


def get_published_posts(queryset):
    """
    Возвращает опубликованные посты с аннотацией количества комментариев
    и сортировкой по дате публикации.
    """
    return (
        queryset
        .filter(
            is_published=True,
            pub_date__lte=Now(),
            category__is_published=True,
        )
        .select_related('author')
        .annotate(comment_count=Count('comments'))
        .order_by('-pub_date')
    )


def get_posts_with_comments(queryset):
    """
    Возвращает посты с аннотацией количества комментариев,
    сортированные по дате публикации.
    """
    return (
        queryset
        .select_related('author')
        .annotate(comment_count=Count('comments'))
        .order_by('-pub_date')
    )
