from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.timezone import now
from django.http import HttpResponseForbidden
from .models import Room, RoomParticipant
import uuid

@login_required
def start_stream(request):
    """配信を開始するビュー"""
    if request.method == "POST":
        # フォームから入力されたルームIDを取得
        room_id = request.POST.get("room_id")
        is_private = request.POST.get("is_private", "off") == "on"

        # ルームIDが未入力の場合のエラーハンドリング
        if not room_id:
            return render(request, "chat/start_stream.html", {"error": "ルームIDを入力してください。"})

        # 既に同じroom_idが存在する場合のエラーハンドリング
        if Room.objects.filter(room_id=room_id).exists():
            return render(request, "chat/start_stream.html", {"error": "このルームIDは既に使用されています。"})


        # ルームの作成
        room = Room.objects.create(
            host=request.user,
            room_id=room_id,
            is_private=is_private,
            start_time=now()
        )

        # RoomParticipantを作成して参加者として追加
        RoomParticipant.objects.create(
            room=room,
            user=request.user,
            is_host=True,  # ホストフラグを追加
        )

        # ルームページにリダイレクト
        return redirect("chat:room", room_id=room.room_id)

    return render(request, "chat/start_stream.html")


@login_required
def room(request, room_id):
    """ルームの詳細を表示するビュー"""
    room = get_object_or_404(Room, room_id=room_id)
    return render(request, 'chat/room.html', {'room': room})


@login_required
def join_room(request, room_id):
    """ルームに参加するビュー"""
    user_room = get_object_or_404(Room, room_id=room_id, end_time__isnull=True)

    if user_room.is_private and not request.POST.get("room_key") == user_room.room_id:
        return HttpResponseForbidden("正しいルームキーを入力してください。")

    # 参加者のカウントを更新
    user_room.participant_count += 1
    user_room.save()

    return render(request, "chat/room.html", {"room": user_room})


@login_required
def end_stream(request, room_id):
    """配信を終了するビュー（配信者のみ）"""
    user_room = get_object_or_404(Room, room_id=room_id, host=request.user, end_time__isnull=True)
    user_room.end_time = now()
    user_room.save()
    return redirect("chat:chat_home")


@login_required
def leave_room(request, room_id):
    """ルームから退出するビュー"""
    room = get_object_or_404(Room, room_id=room_id)
    # 必要ならここでユーザーの退出処理を行う
    return redirect('chat:chat_home')  # ルーム退出後にホームにリダイレクト


@login_required
def chat_home(request):
    """配信中のルーム一覧を表示するビュー"""
    live_rooms = Room.objects.filter(end_time__isnull=True).order_by("-start_time")
    return render(request, "chat/chat.html", {"live_rooms": live_rooms})