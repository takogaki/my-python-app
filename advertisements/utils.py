from .models import Advertisement


def get_random_advertisements(placement):
    """
    指定された掲載場所の有効な広告を取得する
    """

    return list(
        Advertisement.objects.filter(
            is_active=True
        ).filter(
            placement__in=[placement, "both"]
        ).order_by("?")
    )