from pathlib import Path
import os
import dj_database_url
from dotenv import load_dotenv
load_dotenv()

# ==============================
# 基本設定
# ==============================
BASE_DIR = Path(__file__).resolve().parent.parent

DJANGO_ENV = os.environ.get("DJANGO_ENV", "development")
DEBUG = os.environ.get("DJANGO_DEBUG") == "True"

# DEBUG = True

# ★ SECRET_KEY は Render の Environment Variables からのみ取得
# ★ fallback / dotenv / 二重定義は一切しない
SECRET_KEY = os.environ.get(
    "DJANGO_SECRET_KEY",
    "dev-secret-key-unsafe"
)

ALLOWED_HOSTS = [
    "localhost",
    "127.0.0.1",
    "my-python-app-0t2k.onrender.com",
    ".onrender.com",
]

# blog/security.py（新規作成を推奨）

ALLOWED_VIDEO_DOMAINS = {
    "youtube.com",
    "www.youtube.com",
    "youtu.be",
    "tiktok.com",
    "www.tiktok.com",
    "instagram.com",
    "www.instagram.com",
    "twitter.com",
    "www.twitter.com",
    "x.com",
    "www.x.com",
    "facebook.com",
    "www.facebook.com",
}

# Render 固有ホスト
RENDER_EXTERNAL_HOSTNAME = os.environ.get("RENDER_EXTERNAL_HOSTNAME")
if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)

RENDER_INTERNAL_HOSTNAME = os.environ.get("RENDER_INTERNAL_HOSTNAME")
if RENDER_INTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_INTERNAL_HOSTNAME)

# ----------------------------------
# セキュリティ設定
# ----------------------------------
if DJANGO_ENV == "production":
    SECURE_SSL_REDIRECT = True
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

    SESSION_COOKIE_SAMESITE = "None"
    CSRF_COOKIE_SAMESITE = "None"

    CSRF_TRUSTED_ORIGINS = [
        "https://my-python-app-0t2k.onrender.com",
    ]

    SECURE_BROWSER_XSS_FILTER = True
    X_FRAME_OPTIONS = "SAMEORIGIN"
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

else:
    SECURE_SSL_REDIRECT = False
    SECURE_PROXY_SSL_HEADER = None

    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SECURE = False

    SESSION_COOKIE_SAMESITE = "Lax"
    CSRF_COOKIE_SAMESITE = "Lax"

    CSRF_TRUSTED_ORIGINS = [
        "http://127.0.0.1:8000",
        "http://localhost:8000",
    ]


# ⚠️ これだけでOK。import cloudinary は不要
CLOUDINARY_STORAGE = {
    "CLOUD_NAME": os.environ.get("CLOUDINARY_CLOUD_NAME"),
    "API_KEY": os.environ.get("CLOUDINARY_API_KEY"),
    "API_SECRET": os.environ.get("CLOUDINARY_API_SECRET"),
}


# ----------------------------------
# アプリケーション定義
# ----------------------------------
INSTALLED_APPS = [
    "cloudinary_storage",
    "cloudinary",
    "csp",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "whitenoise.runserver_nostatic",
    "django.contrib.staticfiles",
    "accounts.apps.AccountsConfig",
    "diary.apps.DiaryConfig",
    "blog.apps.BlogConfig",
    "chat",
    "user_messages",
    "django_extensions",
]

WHITENOISE_KEEP_ONLY_HASHED_FILES = True

DEFAULT_FILE_STORAGE = "cloudinary_storage.storage.MediaCloudinaryStorage"

MIDDLEWARE = [
    "csp.middleware.CSPMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
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

# ----------------------------------
# データベース
# ----------------------------------
if "DATABASE_URL" in os.environ:
    DATABASES = {
        "default": dj_database_url.config(
            conn_max_age=600,
            ssl_require=True
        )
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

# ----------------------------------
# 認証
# ----------------------------------
AUTH_USER_MODEL = "accounts.CustomUser"

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LOGIN_URL = "/accounts/login/"
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/accounts/login/"

# ----------------------------------
# 言語・時間
# ----------------------------------
LANGUAGE_CODE = "ja"
TIME_ZONE = "Asia/Tokyo"
USE_I18N = True
USE_TZ = True

# ----------------------------------
# 静的ファイル
# ----------------------------------
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATICFILES_STORAGE = "whitenoise.storage.StaticFilesStorage"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# ----------------------------------
# メール
# ----------------------------------
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD")
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

# ----------------------------------
# その他
# ----------------------------------
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# =========================
# Content Security Policy (django-csp 4.x+)
# =========================

CONTENT_SECURITY_POLICY = {
    "DIRECTIVES": {
        "default-src": (
            "'self'",
        ),

        "frame-src": (
            "'self'",
            "https://www.youtube.com",
            "https://www.youtube-nocookie.com",
            "https://www.tiktok.com",
            "https://www.instagram.com",
            "https://www.facebook.com",
            "https://platform.twitter.com",
        ),

        "script-src": (
            "'self'",
            "https://www.youtube.com",
            "https://www.tiktok.com",
            "https://www.instagram.com",
            "https://platform.twitter.com",
            "https://connect.facebook.net",
        ),

        "style-src": (
            "'self'",
            "'unsafe-inline'",  # Instagram / TikTok embed 必須
        ),

        "img-src": (
            "'self'",
            "data:",
            "https:",
        ),
    }
}