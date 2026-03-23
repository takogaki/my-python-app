from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from diary.views import index
from django.contrib.sitemaps.views import sitemap
from .sitemaps import StaticViewSitemap

sitemaps = {
    'static': StaticViewSitemap,
}

urlpatterns = [
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}),
    path("", index, name="index"),   # ← トップページ
    path('user_messages/', include('user_messages.urls')),  
    path("admin/", admin.site.urls),
    path("diary/", include("diary.urls")),
    path('blog/', include('blog.urls')),  
    path('accounts/', include('accounts.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
    path("videochat/", include("videochat.urls")),
    path("notifications/", include("notifications.urls")),
    path('reels/', include('reels.urls')),
] 

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )
