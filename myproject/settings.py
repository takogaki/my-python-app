from pathlib import Path
import os
from dotenv import load_dotenv
load_dotenv()

# ==============================
# .envファイルを自動選択読み込み
# ==============================
BASE_DIR = Path(__file__).resolve().parent.parent
env_file = BASE_DIR / (".env.production" if os.getenv("DJANGO_ENV") == "production" else ".env.development")
load_dotenv(env_file)

# ==============================
# 基本設定
# ==============================
DJANGO_ENV = os.getenv("DJANGO_ENV", "development")
DEBUG = os.getenv("DJANGO_DEBUG", "True") == "True"
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "default_secret_key")

# ----------------------------------
# セキュリティ設定
# ----------------------------------
if DJANGO_ENV == "production":
    SECURE_SSL_REDIRECT = True
    CSRF_COOKIE_SECURE = True
    SESSION_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
else:
    # 開発環境ではHTTPSを無効化
    SECURE_SSL_REDIRECT = False
    CSRF_COOKIE_SECURE = False
    SESSION_COOKIE_SECURE = False
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True

# ----------------------------------
# アプリケーション定義
# ----------------------------------
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "diary.apps.DiaryConfig",
    "blog.apps.BlogConfig",
    "chat",
    "channels",
    "accounts",
    "user_messages",
    "django_extensions",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "myproject.middleware.VisitorTrackingMiddleware",
]

ROOT_URLCONF = "myproject.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "accounts.context_processors.visitor_counts",
            ],
        },
    },
]

WSGI_APPLICATION = "myproject.wsgi.application"
ASGI_APPLICATION = "myproject.routing.application"

# ----------------------------------
# Channels（リアルタイム通信設定）
# ----------------------------------
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {"hosts": [("127.0.0.1", 6379)]},
    },
}

# ----------------------------------
# データベース設定
# ----------------------------------
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": os.getenv("DB_NAME", "diary"),
        "USER": os.getenv("DB_USER", "takogaki"),
        "PASSWORD": os.getenv("DB_PASSWORD", "atjwbg28509224"),
        "HOST": os.getenv("DB_HOST", "localhost"),
        "PORT": int(os.getenv("DB_PORT", 3306)),
        "OPTIONS": {"charset": "utf8mb4"},
    }
}

# ----------------------------------
# 認証・パスワード
# ----------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]
AUTH_USER_MODEL = "accounts.CustomUser"

# ----------------------------------
# 言語・タイムゾーン
# ----------------------------------
LANGUAGE_CODE = "ja"
TIME_ZONE = "Asia/Tokyo"
USE_I18N = True
USE_TZ = True

# ----------------------------------
# 静的・メディアファイル
# ----------------------------------
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# ----------------------------------
# CORS / CSRF
# ----------------------------------
CSRF_TRUSTED_ORIGINS = [
    "http://127.0.0.1:8000",
    "http://localhost:8000",
]
ALLOWED_HOSTS = ["127.0.0.1", "localhost", "0.0.0.0"]
if DJANGO_ENV == "development":
    ALLOWED_HOSTS = ["*"]

# ----------------------------------
# メール設定
# ----------------------------------
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD", "")
DEFAULT_FROM_EMAIL = os.getenv("DJANGO_EMAIL", "noreply@example.com")

# ----------------------------------
# リダイレクト設定
# ----------------------------------
LOGIN_URL = "/accounts/login/"
LOGIN_REDIRECT_URL = "/diary/"
LOGOUT_REDIRECT_URL = "/accounts/login/"
SIGNUP_REDIRECT_URL = "/diary/"

# ----------------------------------
# デフォルト主キー設定
# ----------------------------------
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


if DJANGO_ENV == "development":
    SECURE_SSL_REDIRECT = False
    SECURE_PROXY_SSL_HEADER = None
