from django.urls import path
from . import views


app_name = "videochat"


urlpatterns = [

    # ==================================================
    # LIVE一覧
    # ==================================================

    path(
        "",
        views.room_list,
        name="room_list",
    ),


    # ==================================================
    # LIVE作成
    # ==================================================

    path(
        "start/",
        views.start_room,
        name="start",
    ),


    # ==================================================
    # 配信者用LIVE画面
    # ==================================================

    path(
        "<slug:room_slug>/start/",
        views.room_start,
        name="room_start",
    ),


    # ==================================================
    # LIVE視聴
    # ==================================================

    path(
        "join/<slug:room_slug>/",
        views.room_join,
        name="room_join",
    ),


    # ==================================================
    # パスワード
    # ==================================================

    path(
        "password/<slug:room_slug>/",
        views.room_password,
        name="room_password",
    ),


    # ==================================================
    # LIVE管理
    # ==================================================

    path(
        "<slug:room_slug>/manage/",
        views.room_manage,
        name="room_manage",
    ),


    # ==================================================
    # 参加者承認
    # ==================================================

    path(
        "<slug:room_slug>/approve/<int:user_id>/",
        views.approve_participant,
        name="approve_participant",
    ),


    # ==================================================
    # LIVE参加申請
    # ==================================================

    path(
        "<slug:room_slug>/request-participation/",
        views.request_participation,
        name="request_participation",
    ),


    # ==================================================
    # LIVE終了
    # ==================================================

    path(
        "<slug:room_slug>/end/",
        views.room_end,
        name="room_end",
    ),


    # ==================================================
    # 強制終了
    # ==================================================

    path(
        "force-close/<int:room_id>/",
        views.force_close,
        name="force_close",
    ),


    # ==================================================
    # ホストHeartbeat
    # ==================================================

    path(
        "videochat/<slug:room_slug>/heartbeat/",
        views.room_heartbeat,
        name="room_heartbeat",
    ),
]