from .models import RecruitChatMessage, RecruitChatRead, RecruitChatRoom


def recruit_unread_count(request):

    if not request.user.is_authenticated:
        return {
            "recruit_unread_total": 0,
        }

    total = 0

    rooms = RecruitChatRoom.objects.filter(
        recruit__user=request.user
    )

    # 応募者として参加しているチャットも対象
    participant_rooms = RecruitChatRoom.objects.filter(
        recruit__participants__user=request.user,
        recruit__participants__status="approved",
    )

    rooms = rooms | participant_rooms

    rooms = rooms.distinct()

    for room in rooms:

        read_state = RecruitChatRead.objects.filter(
            room=room,
            user=request.user,
        ).first()

        messages = RecruitChatMessage.objects.filter(
            room=room,
        ).exclude(
            user=request.user
        )

        if read_state and read_state.last_read_message_id:

            messages = messages.filter(
                created_at__gt=
                read_state.last_read_message.created_at
            )

        total += messages.count()

    return {
        "recruit_unread_total": total,
    }