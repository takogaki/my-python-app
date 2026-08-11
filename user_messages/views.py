from django.db import transaction
from django.core.mail import EmailMessage
from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from .forms import ReplyMessageForm
from .models import Message
from accounts.models import CustomUser, Match
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden, JsonResponse
from django.db.models import Max, Q, Count
from django.contrib.auth import get_user_model
from django.contrib import messages
from notifications.models import Notification
from datetime import timedelta
from django.utils import timezone
from django.views.decorators.cache import never_cache
from django.utils.timezone import now
from accounts.utils import save_page_log

User = get_user_model()


@login_required
def message_box(request):
    # =========================
    # ページログ保存
    # =========================
    if request.user.is_authenticated:
        save_page_log(request, "message_box")

    user = request.user

    all_messages = Message.objects.filter(
        Q(sender=user) | Q(recipient=user)
    ).order_by("-sent_at")

    conversations = {}

    for msg in all_messages:
        partner = msg.recipient if msg.sender == user else msg.sender

        if partner.id not in conversations:
            conversations[partner.id] = {
                "user": partner,
                "last_message": msg,
                "unread_count": 0,
            }

        # 未読カウント（相手→自分のみ）
        if msg.recipient == user and not msg.is_read:
            conversations[partner.id]["unread_count"] += 1

    context = {
        "conversations": conversations.values()
    }

    return render(request, "message/message_box.html", context)


@never_cache
@login_required
def send_message(request, username):

    sender = request.user

    recipient = get_object_or_404(
        User,
        username=username
    )

    # =========================
    # 🔐 相互LIKE（Match）確認
    # =========================
    is_matched = Match.objects.filter(
        Q(user1=sender, user2=recipient) |
        Q(user1=recipient, user2=sender)
    ).exists()

    # =========================
    # ❌ MatchしていなければDM不可
    # =========================
    if not is_matched:
        return render(
            request,
            "message/not_matched.html",
            {
                "target_user": recipient
            },
            status=403
        )

    # =========================
    # 🔥 POST（送信処理）
    # =========================
    if request.method == "POST":

        content = request.POST.get(
            "message",
            ""
        ).strip()

        if content:
            Message.objects.create(
                sender=sender,
                recipient=recipient,
                content=content
            )

    # =========================
    # 🔥 未読 → 既読
    # =========================
    Message.objects.filter(
        sender=recipient,
        recipient=sender,
        is_read=False
    ).update(
        is_read=True,
        read_at=now()
    )

    # =========================
    # 🔥 チャット履歴取得
    # =========================
    chat_messages = Message.objects.filter(
        Q(sender=sender, recipient=recipient) |
        Q(sender=recipient, recipient=sender)
    ).order_by("sent_at")

    # =========================
    # 🔥 最後の既読メッセージ
    # =========================
    last_read_message = Message.objects.filter(
        sender=sender,
        recipient=recipient,
        is_read=True
    ).order_by("-sent_at").first()

    return render(
        request,
        "message/send_message.html",
        {
            "recipient": recipient,
            "messages": chat_messages,
            "last_read_message": last_read_message,
        }
    )


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

    # =========================
    # 🔐 相互LIKE（Match）確認
    # =========================
    other_user = original.sender

    is_matched = Match.objects.filter(
        Q(user1=request.user, user2=other_user) |
        Q(user1=other_user, user2=request.user)
    ).exists()

    # =========================
    # ❌ Match解除済みなら返信不可
    # =========================
    if not is_matched:
        return render(
            request,
            "message/not_matched.html",
            {
                "target_user": other_user
            },
            status=403
        )

    # =========================
    # 🔥 返信処理
    # =========================
    if request.method == "POST":

        form = ReplyMessageForm(request.POST)

        if form.is_valid():

            reply = form.save(commit=False)

            reply.sender = request.user
            reply.recipient = other_user

            reply.save()

            return redirect(
                "user_messages:message_detail",
                pk=original.pk
            )

    else:
        form = ReplyMessageForm()

    return render(
        request,
        "user_messages/message_reply.html",
        {
            "form": form,
            "original": original,
        }
    )