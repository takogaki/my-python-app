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

    # 🤝 新規募集作成
    path("recruit/create/", views.recruit_create, name="recruit_create"),

    # 🤝 募集詳細
    path("recruit/<int:pk>/", views.recruit_detail, name="recruit_detail"),

    #🤝 募集編集
    path("recruit/<int:pk>/edit/", views.recruit_edit, name="recruit_edit"),

    #🤝 募集削除
    path("recruit/<int:pk>/close/", views.close_recruit, name="close_recruit"),

    #🤝 募集キャンセル
    path("recruit/<int:pk>/cancel/", views.cancel_recruit, name="cancel_recruit"),

    # 🤝 募集再開
    path("recruit/<int:pk>/reopen/", views.reopen_recruit, name="reopen_recruit"),

    # 🤝 募集応募
    path("recruit/<int:pk>/apply/", views.apply_recruit, name="apply_recruit"),

    # =========================
    # 🤝 募集応募者管理
    # =========================
    path("recruit-management/", views.recruit_management, name="recruit_management"),

    path("recruit/<int:pk>/participants/", views.recruit_participants, name="recruit_participants"),

    path("recruit/participant/<int:pk>/approve/", views.approve_recruit_participant, name="approve_recruit_participant"),

    path("recruit/participant/<int:pk>/reject/", views.reject_recruit_participant, name="reject_recruit_participant"),

    #=========================
    # 🤝 募集チャット
    #=========================
    path("recruit/<int:pk>/chat/", views.recruit_chat, name="recruit_chat"),
]