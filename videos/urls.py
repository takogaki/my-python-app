from django.urls import path
from . import views

urlpatterns = [
    # 動画フィードとアップロード
    path("feed/", views.feed, name="feed"),
    path("upload/", views.upload, name="video_upload"),

    # 🔥 いいねAPI
    path("like/<int:post_id>/", views.toggle_like, name="toggle_like"),

    # 🔥 コメントAPI
    path("comments/<int:post_id>/", views.get_comments, name="get_comments"),
    path("comment/add/<int:post_id>/", views.add_comment, name="add_comment"),

    # 🔥 ユーザーフィード
    path("user/<str:username>/", views.user_video_feed, name="video_feed_user"),
]