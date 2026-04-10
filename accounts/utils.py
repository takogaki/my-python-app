def profile_completion(profile):
    score = 0

    # =========================
    # 基本情報
    # =========================
    if profile.profile_image:
        score += 10

    if profile.bio:
        score += 10

    # =========================
    # タグ（重要）
    # =========================
    tag_count = profile.profile_tags.count()

    if tag_count >= 5:
        score += 10
    if tag_count >= 10:
        score += 10
    if tag_count >= 20:
        score += 10
    if tag_count >= 30:
        score += 10

    # =========================
    # 詳細情報
    # =========================
    if getattr(profile, "drinking", None):
        score += 5

    if getattr(profile, "smoking", None):
        score += 5

    if getattr(profile, "job", None):
        score += 5

    if getattr(profile, "income", None):
        score += 5

    if hasattr(profile.user, "birth_date") and profile.user.birth_date:
        score += 5

    return min(score, 100)


def compatibility(user1, user2):

    if not hasattr(user1, "profile") or not hasattr(user2, "profile"):
        return 0

    tags1 = {
        pt.tag_id: pt.level
        for pt in user1.profile.profile_tags.all()
    }

    tags2 = {
        pt.tag_id: pt.level
        for pt in user2.profile.profile_tags.all()
    }

    score = 0

    for tag_id in tags1:
        if tag_id in tags2:
            score += 10

            diff = abs(tags1[tag_id] - tags2[tag_id])
            score += max(0, 3 - diff)  # ← マイナス防止

    return score