from django.db import models
from django.contrib.auth import get_user_model

from .constants import MAX_TITLE_LENGTH


User = get_user_model()


class Category(models.Model):
    """Модель для описания тематической категории публикации."""

    title = models.CharField(
        max_length=MAX_TITLE_LENGTH,
        verbose_name="Заголовок",
        help_text="Введите название категории.",
    )
    description = models.TextField(
        verbose_name="Описание",
        help_text="Введите описание категории.",
    )
    slug = models.SlugField(
        unique=True,
        verbose_name="Идентификатор",
        help_text=(
            "Идентификатор страницы для URL; разрешены символы латиницы, "
            "цифры, дефис и подчёркивание."
        ),
    )
    is_published = models.BooleanField(
        default=True,
        verbose_name="Опубликовано",
        help_text="Снимите галочку, чтобы скрыть публикацию.",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Добавлено",
    )

    class Meta:
        verbose_name = "категория"
        verbose_name_plural = "Категории"

    def __str__(self):
        return self.title


class Location(models.Model):
    """Модель для географической метки публикации."""

    name = models.CharField(
        max_length=MAX_TITLE_LENGTH,
        verbose_name="Название места",
        help_text="Введите название места.",
    )
    is_published = models.BooleanField(
        default=True,
        verbose_name="Опубликовано",
        help_text="Снимите галочку, чтобы скрыть публикацию.",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Добавлено",
    )

    class Meta:
        verbose_name = "местоположение"
        verbose_name_plural = "Местоположения"

    def __str__(self):
        return self.name


class Post(models.Model):
    """Модель для описания публикации в блоге."""

    title = models.CharField(
        max_length=MAX_TITLE_LENGTH,
        verbose_name="Название публикации",
        help_text="Введите заголовок публикации.",
    )
    text = models.TextField(
        verbose_name="Текст",
        help_text="Введите текст публикации.",
    )
    pub_date = models.DateTimeField(
        verbose_name="Дата и время публикации",
        help_text=(
            "Если установить дату и время в будущем — "
            "можно делать отложенные публикации."
        ),
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="posts",
        verbose_name="Автор публикации",
    )
    location = models.ForeignKey(
        "Location",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="posts",
        verbose_name="Местоположение",
    )
    category = models.ForeignKey(
        "Category",
        on_delete=models.SET_NULL,
        null=True,
        related_name="posts",
        verbose_name="Категория",
    )
    image = models.ImageField(
        upload_to="post_images/",
        null=True,
        blank=True,
        verbose_name="Изображение",
        help_text="Прикрепите изображение для публикации.",
    )
    is_published = models.BooleanField(
        default=True,
        verbose_name="Опубликовано",
        help_text="Снимите галочку, чтобы скрыть публикацию.",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Добавлено",
    )

    class Meta:
        verbose_name = "публикация"
        verbose_name_plural = "Публикации"

    def __str__(self):
        return self.title


class Comment(models.Model):
    """Модель комментария к публикации."""

    post = models.ForeignKey(
        Post,
        related_name="comments",
        on_delete=models.CASCADE,
        verbose_name="Публикация",
        help_text="Публикация, к которой относится комментарий.",
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="comments",
        verbose_name="Автор комментария",
        help_text="Пользователь, который оставил комментарий.",
    )
    text = models.TextField(
        verbose_name="Текст комментария",
        help_text="Введите текст комментария.",
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата и время публикации",
        help_text="Дата и время, когда был оставлен комментарий.",
    )

    class Meta:
        verbose_name = "Комментарий"
        verbose_name_plural = "Комментарии"
        ordering = ["pub_date"]

    def __str__(self):
        return f"Комментарий от {self.author.username} на {self.post.title}"
