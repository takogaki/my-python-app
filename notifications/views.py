from django.shortcuts import render
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Notification

@login_required
def open_notification(request, pk):
    notification = get_object_or_404(
        Notification,
        pk=pk,
        recipient=request.user
    )

    # 移動先URLを先に退避
    target_url = notification.target_url

    # 🔥 通知を削除（ここが重要）
    notification.delete()

    return redirect(target_url)