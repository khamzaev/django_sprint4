from django.urls import path

from . import views


app_name = 'blog'

urlpatterns = [
    # Общие страницы
    path('', views.index, name='index'),

    # Управление пользователями
    path('register/', views.UserRegistrationView.as_view(), name='register'),
    path('profile/<str:username>/', views.UserProfileView.as_view(), name='profile'),
    path('profile/edit/', views.UserProfileEditView.as_view(), name='profile_edit'),
    path('password_change/', views.UserPasswordChangeView.as_view(), name='password_change'),

    # Посты
    path('create/', views.PostCreateView.as_view(), name='post_create'),
    path(
        'posts/<int:id>/',
        views.PostDetailView.as_view(),
        name='post_detail'
    ),
    path(
        'posts/<int:id>/edit/',
        views.PostEditView.as_view(),
        name='post_edit'
    ),
    path(
        'posts/<int:post_id>/delete/',
        views.PostDeleteView.as_view(),
        name='post_delete'
    ),

    # Комментарии
    path(
        'posts/<int:post_id>/comment/',
        views.add_comment,
        name='add_comment'
    ),
    path(
        'posts/<int:post_id>/edit_comment/<int:comment_id>/',
        views.edit_comment,
        name='edit_comment'
    ),
    path(
        'posts/<int:post_id>/delete_comment/<int:comment_id>/',
        views.CommentDeleteView.as_view(),
        name='comment_delete'
    ),

    # Категории
    path(
        'category/<slug:category_slug>/',
        views.CategoryPostListView.as_view(),
        name='category_posts'
    ),
]

