from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from diary.views import index
from videos.views import feed
from django.contrib.sitemaps.views import sitemap
from .sitemaps import StaticViewSitemap
from django.views.generic import TemplateView
from django.views.generic.base import RedirectView

sitemaps = {
    'static': StaticViewSitemap,
}

urlpatterns = [
    path("robots.txt", TemplateView.as_view(template_name="robots.txt", content_type="text/plain")),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}),

    path(
        "service-worker.js",
        TemplateView.as_view(
            template_name="service-worker.js",
            content_type="application/javascript"
        ),
    ),

    # 🔥 トップをfeedにする
    path("", RedirectView.as_view(url="/accounts/app/")),
    path("feed/", feed, name="feed"),

    # 🔥 indexは別URLに逃がす
    path("index/", index, name="index"),

    path('user_messages/', include('user_messages.urls')),  
    path("admin/", admin.site.urls),
    path("diary/", include("diary.urls")),
    path('blog/', include('blog.urls')),  
    path('accounts/', include('accounts.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
    path("videochat/", include("videochat.urls")),
    path("notifications/", include("notifications.urls")),
    path("videos/", include("videos.urls")),

    # 位置情報 GPS
    path("locations/", include("locations.urls")),

    # ランダム通話
    path("random-call/", include("random_call.urls")),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )
