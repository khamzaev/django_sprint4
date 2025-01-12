from django.db.models import Count
from django.db.models.functions import Now


def get_post_queryset(objects_manager):
    return (
        objects_manager
        .filter(
            is_published=True,
            pub_date__lte=Now(),
            category__is_published=True
        )
        .select_related('author')
        .prefetch_related('category', 'location')
        .order_by('-pub_date')
        .annotate(comment_count=Count('comments'))
    )