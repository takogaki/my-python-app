import json

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db.models import Q
from django.utils import timezone

from .models import UserLocation
from .utils import calculate_distance_km

from videos.models import Recruit


# ==================================================
# 📍 現在地を保存
# ==================================================

@login_required
@require_POST
def update_location(request):

    try:

        data = json.loads(request.body)

        latitude = float(data.get("latitude"))
        longitude = float(data.get("longitude"))

    except (TypeError, ValueError, json.JSONDecodeError):

        return JsonResponse(
            {
                "success": False,
                "error": "位置情報が正しくありません。",
            },
            status=400,
        )


    # ==================================================
    # GPSとして現実的な範囲か確認
    # ==================================================

    if not -90 <= latitude <= 90:

        return JsonResponse(
            {
                "success": False,
                "error": "緯度が不正です。",
            },
            status=400,
        )


    if not -180 <= longitude <= 180:

        return JsonResponse(
            {
                "success": False,
                "error": "経度が不正です。",
            },
            status=400,
        )


    # ==================================================
    # 📍 UserLocationを更新
    # ==================================================

    location, created = UserLocation.objects.update_or_create(

        user=request.user,

        defaults={
            "latitude": latitude,
            "longitude": longitude,
            "is_active": True,
        },

    )


    return JsonResponse(
        {
            "success": True,
            "created": created,
            "latitude": location.latitude,
            "longitude": location.longitude,
        }
    )


# ==================================================
# 📍 近くの募集
# ==================================================

@login_required
def nearby_recruits(request):

    try:

        user_location = UserLocation.objects.get(
            user=request.user,
            is_active=True,
        )

    except UserLocation.DoesNotExist:

        return JsonResponse(
            {
                "success": False,
                "message": "現在地が登録されていません。",
            },
            status=400,
        )


    # ==================================================
    # 🤝 募集中の募集を取得
    # ==================================================

    recruits = (
        Recruit.objects
        .filter(
            is_active=True,
            status="open",
            latitude__isnull=False,
            longitude__isnull=False,
        )
        .filter(
            Q(expires_at__isnull=True) |
            Q(expires_at__gt=timezone.now())
        )
        .select_related("user")
    )


    nearby = []


    # ==================================================
    # 📏 距離計算
    # ==================================================

    for recruit in recruits:

        # ==================================================
        # 🚻 募集対象性別チェック
        # ==================================================

        if recruit.target_gender == "male":

            # 男性のみ → M のユーザーだけ
            if request.user.gender != "M":
                continue


        elif recruit.target_gender == "female":

            # 女性のみ → F のユーザーだけ
            if request.user.gender != "F":
                continue

        # ==================================================
        # 📏 距離計算
        # ==================================================
        distance = calculate_distance_km(

            user_location.latitude,
            user_location.longitude,

            recruit.latitude,
            recruit.longitude,

        )

        # 50kmを超える募集は表示しない
        if distance > 30:
            continue


        nearby.append(
        {
            "id": recruit.id,
            "title": recruit.title,
            "place": recruit.place,
            "distance": round(distance, 1),

            # 👤 ユーザー情報
            "username": recruit.user.username,
            "profile_image": recruit.user.get_profile_image(),

            # 🚻 性別
            "gender": recruit.user.gender,
            
            # 画像
            "image": recruit.image.url if recruit.image else None,
        }
    )


    # ==================================================
    # 📍 近い順
    # ==================================================

    nearby.sort(
        key=lambda item: item["distance"]
    )


    return JsonResponse(
        {
            "success": True,
            "results": nearby,
        }
    )

