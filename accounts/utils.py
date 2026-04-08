def compatibility(user1, user2):
    # プロフィールが無い場合
    if not hasattr(user1, "profile") or not hasattr(user2, "profile"):
        return 0

    tags1 = set(user1.profile.tags.values_list("id", flat=True))
    tags2 = set(user2.profile.tags.values_list("id", flat=True))

    # タグ未設定対策
    if not tags1 or not tags2:
        return 0

    common = tags1 & tags2

    # スコア（そのまま数）
    return len(common)


def profile_completion(profile):
    score = 0
    total = 8  # 項目数

    if profile.profile_image:
        score += 1
    if profile.bio:
        score += 1
    if profile.tags.exists():
        score += 1
    if profile.drinking:
        score += 1
    if profile.smoking:
        score += 1
    if profile.job:
        score += 1
    if profile.income:
        score += 1
    if profile.user.birth_date:
        score += 1

    return int((score / total) * 100)

# 共通タグ + レベル差でスコア算出
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
            score += (3 - diff)

    return score