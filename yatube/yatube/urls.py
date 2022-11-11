from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from about.apps import AboutConfig
from posts.apps import PostsConfig
from users.apps import UsersConfig

handler500 = 'core.views.server_failure'
handler403 = 'core.views.csrf_failure'

urlpatterns = [
    path('about/', include('about.urls', namespace=AboutConfig.name)),
    path('admin/', admin.site.urls),
    path('auth/', include('users.urls', namespace=UsersConfig.name)),
    path('auth/', include('django.contrib.auth.urls')),
    path('', include('posts.urls', namespace=PostsConfig.name)),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT,
    )
