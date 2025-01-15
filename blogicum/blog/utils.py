from django.db.models.functions import Now
from django.db.models import Count


def get_published_posts(queryset):
    """
    Возвращает опубликованные посты с аннотацией количества комментариев
    и сортировкой по дате публикации.
    """
    return (
        get_posts_with_comments(queryset)
        .filter(
            is_published=True,
            pub_date__lte=Now(),
            category__is_published=True,
        )
    )


def get_posts_with_comments(queryset):
    """
    Возвращает посты с аннотацией количества комментариев,
    сортированные по дате публикации.
    """
    return (
        queryset
        .select_related('author', 'category', 'location')
        .annotate(comment_count=Count('comments'))
        .order_by('-pub_date')
    )
