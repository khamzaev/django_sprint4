from django.db.models.functions import Now
from django.db.models import Count


def filter_published_posts(queryset):
    """
    Фильтрует опубликованные посты, у которых дата публикации уже прошла,
    категория опубликована и посты сортируются по дате публикации от новых к старым.
    """
    return queryset.filter(
        is_published=True,
        pub_date__lte=Now(),
        category__is_published=True,
    ).select_related('author') \
        .prefetch_related('category', 'location') \
        .order_by('-pub_date')



def annotate_posts_with_comments(queryset):
    """
    Добавляет аннотацию количества комментариев к постам
    и сортирует их по дате публикации.
    """
    return (
        queryset
        .select_related('author', 'category', 'location')
        .annotate(comment_count=Count('comments'))
        .order_by('-pub_date')
    )
