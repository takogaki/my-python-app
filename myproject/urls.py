from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from blog.views import frontpage, post_detail



urlpatterns = [
    path('user_messages/', include('user_messages.urls')),  # emailアプリのURLを追加

    path("admin/", admin.site.urls),
    path("diary/", include("diary.urls")),
    path('blog/', include('blog.urls')),  
    path('accounts/', include('accounts.urls')),
    path('', include('django.contrib.auth.urls')),

    #path("", frontpage, name="frontpage"),
    #path("posts/<slug:slug>/", post_detail, name="post_detail"),

    # path('videos/', include('video_platform.urls', namespace='video_platform')),

    path('chat/', include('chat.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)