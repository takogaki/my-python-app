# chat/urls.py
from django.urls import path
from . import views

app_name = "chat"
urlpatterns = [
    path('chat/', views.chat_home, name='chat_home'),  # ホームページ
    path('join/<str:room_id>/', views.join_room, name='join_room'),  # ルームに入室
    path('room/<str:room_id>/', views.room, name='room'),  # ルームの詳細ページ
    path('start/', views.start_stream, name='start_stream'),  # 配信開始 (引数不要)
    path('end_stream/<str:room_id>/', views.end_stream, name='end_stream'),  # 配信終了
    path('leave_room/<str:room_id>/', views.leave_room, name='leave_room'),
]