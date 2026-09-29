from django.shortcuts import render
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Notification
from django.urls import reverse


@login_required
def open_notification(request, pk):

    notification = get_object_or_404(
        Notification,
        pk=pk,
        recipient=request.user
    )

    # =========================
    # 🔔 通知を既読にする
    # =========================

    target_url = notification.target_url

    notification.is_read = True

    notification.save(
        update_fields=["is_read"]
    )

    # =========================
    # ❗ URLが無い場合
    # =========================

    if not target_url:
        return redirect("accounts:mypage")

    return redirect(target_url)