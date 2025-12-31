from django.urls import path
from . import views
# blog/utils.py
import uuid
from django.urls import path
from .views import frontpage

urlpatterns = [
    path("", frontpage, name="frontpage"),
]


def get_device_id(request):
    """
    未ログインユーザー用の一意な端末IDを返す
    """
    device_id = request.COOKIES.get("device_id")
    if device_id:
        return device_id

    return uuid.uuid4().hex



app_name = "blog"
urlpatterns = [
    path('', views.frontpage, name="frontpage"),
    path("posts/create/", views.post_create, name="post_create"),
    path('posts/<slug:slug>/', views.post_detail, name="post_detail"),
]