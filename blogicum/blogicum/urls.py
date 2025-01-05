from django.contrib import admin

from django.urls import path, include

from blog.views import UserRegistrationView

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', include('blog.urls', namespace='blog')),
    path('pages/', include('pages.urls', namespace='pages')),
    path('auth/', include('django.contrib.auth.urls')),
    path('auth/registration/', UserRegistrationView.as_view(), name='registration'),
    path('admin/', admin.site.urls),
]

handler404 = 'pages.views.error_404'
handler500 = 'pages.views.error_500'

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)