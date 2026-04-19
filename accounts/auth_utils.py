from urllib.parse import urlparse

# =========================
# next URL 安全化
# =========================
def safe_next(url):
    if not url:
        return None

    parsed = urlparse(url)

    # 外部URL禁止
    if parsed.netloc:
        return None

    return url


# =========================
# セッション完全リセット
# =========================
def secure_session_reset(request):
    request.session.flush()
    request.session.cycle_key()