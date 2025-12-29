from django.db import transaction
from django.core.mail import EmailMessage
from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from .forms import ReplyMessageForm
from .models import Message
from accounts.models import CustomUser
from django.contrib.auth.decorators import login_required

@login_required
def message_box(request):
    user = request.user
    # メッセージを受信日時が新しい順に取得
    messages = Message.objects.filter(recipient=user).order_by('-sent_at')

    return render(request, 'message/message_box.html', {
        'messages': messages  # メッセージをテンプレートに渡す
    })

@login_required
def send_message(request, username):
    """ユーザーBにメールを送信"""
    recipient = get_object_or_404(CustomUser, username=username)  # ユーザーB
    sender = request.user  # メールを送るユーザーA（ログイン中のユーザー）

    if request.method == "POST":
        message_body = request.POST.get("message")
        message_body = f"{message_body}\n\n※このメールには返信できません。返信はサイト上でお願いいたします。"
        subject = f"{sender.username}さんからのメッセージ"

        # メールの作成
        email = EmailMessage(
            subject=subject,  # 件名
            body=message_body,  # メッセージ本文
            from_email=None,  # `DEFAULT_FROM_EMAIL`を使用
            to=[recipient.email],  # ユーザーBのメールアドレス
            reply_to=[settings.EMAIL_HOST_USER],  # 返信先を固定のメールアドレスに設定
        )

        # トランザクションを使用してメッセージ送信とデータ保存を一緒に処理
        try:
            with transaction.atomic():
                # メール送信
                email.send()

                # メッセージをデータベースに保存
                if sender and recipient:
                    Message.objects.create(
                        sender=sender,
                        recipient=recipient,
                        content=message_body,
                    )

            return redirect("user_messages:success")  # メール送信後に成功ページへ

        except Exception as e:
            print(f"Error occurred: {e}")
            return redirect("user_messages:failure")  # エラーハンドリング（必要に応じて）

    return render(request, "message/send_message.html", {"recipient": recipient})

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
