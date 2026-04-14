from pathlib import Path
import os
import dj_database_url
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

# ==============================
# 🔥 最重要（最初に定義）
# ==============================
DJANGO_ENV = os.environ.get("DJANGO_ENV", "development")
DEBUG = os.environ.get("DJANGO_DEBUG") == "True"

SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "dev-secret-key-unsafe")

# ==============================
# 静的ファイル
# ==============================
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]

# cloudinary対策（必須）
STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"
STATICFILES_STORAGE = "whitenoise.storage.CompressedStaticFilesStorage"

# ==============================
# Cloudinary（画像）
# ==============================
CLOUDINARY_STORAGE = {
    "CLOUD_NAME": os.environ.get("CLOUDINARY_CLOUD_NAME"),
    "API_KEY": os.environ.get("CLOUDINARY_API_KEY"),
    "API_SECRET": os.environ.get("CLOUDINARY_API_SECRET"),
}

# ==============================
# STORAGES（Django4.2以降）
# ==============================
STORAGES = {
    "default": {
        "BACKEND": "cloudinary_storage.storage.MediaCloudinaryStorage",
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}

# ==============================
# ホスト
# ==============================
ALLOWED_HOSTS = [
    "localhost",
    "127.0.0.1",
    "my-python-app-0t2k.onrender.com",
    ".onrender.com",
    ".ngrok-free.app",
]

# ==============================
# CSRF
# ==============================
CSRF_TRUSTED_ORIGINS = [
    "https://my-python-app-0t2k.onrender.com",
    "http://127.0.0.1:8000",
    "http://localhost:8000",
]

# ==============================
# セキュリティ
# ==============================
if DJANGO_ENV == "production":
    SECURE_SSL_REDIRECT = True
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

    SESSION_COOKIE_SAMESITE = "None"
    CSRF_COOKIE_SAMESITE = "None"

else:
    SECURE_SSL_REDIRECT = False

    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SECURE = False

    SESSION_COOKIE_SAMESITE = "Lax"
    CSRF_COOKIE_SAMESITE = "Lax"

# ==============================
# アプリ
# ==============================
INSTALLED_APPS = [
    "csp",
    "channels",
    "cloudinary",
    "cloudinary_storage",

    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    "accounts",
    "diary",
    "blog",
    "videochat",
    "user_messages",
    "notifications",
    "reels",
]

# ==============================
# ミドルウェア
# ==============================
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
    "accounts.middleware.TermsAgreementMiddleware",
]

ROOT_URLCONF = "myproject.urls"

# ==============================
# テンプレート
# ==============================
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "accounts.context_processors.user_count",
                "accounts.context_processors.visitor_counts",
                "videochat.context_processors.unclosed_room_warning",
            ],
        },
    },
]

WSGI_APPLICATION = "myproject.wsgi.application"
ASGI_APPLICATION = "myproject.asgi.application"

# ==============================
# DB
# ==============================
if "DATABASE_URL" in os.environ:
    DATABASES = {
        "default": dj_database_url.config(conn_max_age=600, ssl_require=True)
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

# ==============================
# 認証
# ==============================
AUTH_USER_MODEL = "accounts.CustomUser"

LOGIN_URL = "/accounts/login/"
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/accounts/login/"

# ==============================
# 言語
# ==============================
LANGUAGE_CODE = "ja"
TIME_ZONE = "Asia/Tokyo"
USE_I18N = True
USE_TZ = True

# ==============================
# Redis / セッション
# ==============================
if "REDIS_URL" in os.environ:
    CACHES = {
        "default": {
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": os.environ["REDIS_URL"],
            "OPTIONS": {"CLIENT_CLASS": "django_redis.client.DefaultClient"},
        }
    }

    SESSION_ENGINE = "django.contrib.sessions.backends.cached_db"

else:
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        }
    }

    SESSION_ENGINE = "django.contrib.sessions.backends.db"
    SESSION_COOKIE_AGE = 60 * 60 * 24 * 7
    SESSION_SAVE_EVERY_REQUEST = True

# ==============================
# その他
# ==============================
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"