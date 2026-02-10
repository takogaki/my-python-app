from django.urls import path
from . import views
# blog/utils.py
import uuid
from django.urls import path
from .views import frontpage

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
    path("", frontpage, name="frontpage"),
    path("posts/create/", views.post_create, name="post_create"),
    path('posts/<slug:slug>/', views.post_detail, name="post_detail"),
    path("posts/<slug:slug>/end-live/", views.end_live, name="end_live"),
    path("post/<slug:slug>/delete/", views.delete_post, name="delete_post"),
    path("comment/<int:pk>/delete/", views.delete_comment, name="delete_comment"),
    path("posts/<int:post_id>/save/", views.save_post, name="save_post"),
    path("posts/<int:post_id>/toggle-save/", views.toggle_save_post, name="toggle_save_post"),
]