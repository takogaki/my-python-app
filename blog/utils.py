import uuid


def get_device_id(request):
    """
    未ログインユーザー用の一意な端末識別IDを返す
    ・Cookie があればそれを使う
    ・なければ新しく生成
    """
    device_id = request.COOKIES.get("device_id")

    if not device_id:
        device_id = uuid.uuid4().hex

    return device_id