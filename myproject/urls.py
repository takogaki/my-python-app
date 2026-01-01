from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from blog.views import post_detail
from diary.views import index


urlpatterns = [
    path("", index, name="index"),   # ← トップページ
    path('user_messages/', include('user_messages.urls')),  
    path("admin/", admin.site.urls),
    path("diary/", include("diary.urls")),
    path('blog/', include('blog.urls')),  
    path('accounts/', include('accounts.urls')),
    path('', include('django.contrib.auth.urls')),
    path('chat/', include('chat.urls')),
    path("posts/<slug:slug>/", post_detail, name="post_detail"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )
