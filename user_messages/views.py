from django.db import transaction
from django.core.mail import EmailMessage
from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from .forms import ReplyMessageForm
from .models import Message
from accounts.models import CustomUser, Match
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden, JsonResponse
from django.db.models import Max, Q
from django.contrib.auth import get_user_model
from django.contrib import messages
from notifications.models import Notification
from datetime import timedelta
from django.utils import timezone


User = get_user_model()

@login_required
def message_box(request):
    user = request.user

    # 自分が関わっているメッセージを新しい順に取得
    all_messages = Message.objects.filter(
        Q(sender=user) | Q(recipient=user)
    ).order_by("-sent_at")

    conversation_dict = {}

    for msg in all_messages:
        # 相手を特定
        partner = msg.recipient if msg.sender == user else msg.sender

        # まだその相手が登録されていなければ登録（＝最新メッセージ）
        if partner.id not in conversation_dict:
            conversation_dict[partner.id] = msg

    # 最新メッセージだけのリスト
    messages = list(conversation_dict.values())

    return render(
        request,
        "message/message_box.html",
        {"messages": messages}
    )

@login_required
def send_message(request, username):

    sender = request.user

    # 🔥 年齢認証チェック（最初にやる）
    if sender.verification_status != "verified":
        messages.warning(request, "メッセージ機能は年齢確認後に利用できます")
        return redirect("accounts:kyc_submit")

    recipient = get_object_or_404(User, username=username)

    # 🔐 マッチ確認
    is_matched = Match.objects.filter(
        Q(user1=sender, user2=recipient) |
        Q(user1=recipient, user2=sender)
    ).exists()

    if not is_matched:
        return render(request, "message/not_matched.html", {
            "target_user": recipient
        }, status=403)

    # ✅ 未読 → 既読
    Message.objects.filter(
        sender=recipient,
        recipient=sender,
        is_read=False
    ).update(is_read=True)

    # =========================
    # 🔥 POST処理
    # =========================
    if request.method == "POST":

        # 🔥 二重防御（API直叩き対策）
        if sender.verification_status != "verified":
            return JsonResponse({"error": "KYC required"}, status=403)

        content = request.POST.get("message")

        if content and content.strip():
            Message.objects.create(
                sender=sender,
                recipient=recipient,
                content=content.strip()
            )

            # =========================
            # 🔥 通知追加（ここ）
            # =========================
            recent = Notification.objects.filter(
                recipient=recipient,
                actor=sender,
                type="message",
                created_at__gte=timezone.now() - timedelta(minutes=5)
            ).exists()

            if not recent:
                Notification.objects.create(
                    recipient=recipient,
                    actor=sender,
                    type="message",
                    verb="さんからメッセージが届きました"
                )

    # 🔥 履歴取得
    chat_messages = Message.objects.filter(
        Q(sender=sender, recipient=recipient) |
        Q(sender=recipient, recipient=sender)
    ).order_by("sent_at")

    return render(request, "message/send_message.html", {
        "recipient": recipient,
        "messages": chat_messages
    })


@login_required
def index(request):
    user = request.user
    user_messages = Message.objects.filter(recipient=user)  # 受信したメッセージを取得
    print("User Messages:", user_messages)  # デバッグ用に表示

    form = ReplyMessageForm()

    if request.method == "POST" and 'reply_message' in request.POST:
        form = ReplyMessageForm(request.POST)
        if form.is_valid():
            reply_message = form.cleaned_data['reply_message']
            sender_username = request.POST.get("sender_username")
            sender = get_object_or_404(CustomUser, username=sender_username)

            # メール送信
            reply_message += "\n\n※このメールには返信できません。返信はサイト上でお願いします。"
            email = EmailMessage(
                subject=f"{user.username}さんからの返信",
                body=reply_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[sender.email],
            )
            email.send()

            # メッセージをデータベースに保存
            Message.objects.create(
                sender=user,
                recipient=sender,
                content=reply_message,
            )

            return redirect("user_messages:success")

    return render(request, 'diary/index.html', {
        'user_messages': user_messages,  # メッセージをuser_messagesとして渡す
        'form': form
    })

@login_required
def success(request):
    """送信成功画面のビュー"""
    return render(request, "message/success.html")


@login_required
def failure(request):
    return render(request, "message/failure.html")




@login_required
def message_detail(request, pk):
    message = get_object_or_404(
        Message,
        pk=pk,
        recipient=request.user   # ← 超重要（安全装置）
    )

    # 未読 → 既読
    if not message.is_read:
        message.is_read = True
        message.save(update_fields=["is_read"])

    return render(request, "message/message_detail.html", {
    "message": message,
})



@login_required
def message_reply(request, pk):
    original = get_object_or_404(
        Message,
        pk=pk,
        recipient=request.user
    )

    if request.method == "POST":
        form = ReplyMessageForm(request.POST)
        if form.is_valid():
            reply = form.save(commit=False)
            reply.sender = request.user
            reply.recipient = original.sender
            reply.save()
            return redirect("user_messages:message_detail", pk=original.pk)
    else:
        form = ReplyMessageForm()

    return render(request, "user_messages/message_reply.html", {
        "form": form,
        "original": original,
    })