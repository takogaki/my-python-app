from django.shortcuts import render
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Notification


@login_required
def notification_read(request, pk):
    notification = get_object_or_404(
        Notification,
        pk=pk,
        recipient=request.user
    )

    # 既読にする
    notification.is_read = True
    notification.save(update_fields=["is_read"])

    # 通知が持っているリンク先へ飛ばす
    return redirect(notification.target_url)