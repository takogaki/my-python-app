from pathlib import Path
import os
import dj_database_url
from dotenv import load_dotenv
load_dotenv()

# ==============================
#ローカルサーバー起動
#daphne myproject.asgi:application
# ==============================

BASE_DIR = Path(__file__).resolve().parent.parent

# ----------------------------------
# 静的ファイル
# ----------------------------------
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
# ← 共通staticのみ指定する
STATICFILES_DIRS = [
    BASE_DIR / "static",
]

# 厳しい設定
# STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# 上でデプロイ失敗が続く場合は、少し緩い設定にする（ただしキャッシュ対策は別途必要）
STATICFILES_STORAGE = "whitenoise.storage.CompressedStaticFilesStorage"

# STORAGES = {
#     "default": {
#         "BACKEND": "cloudinary_storage.storage.MediaCloudinaryStorage",
#     },
#     "staticfiles": {
#         "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
#     },
# }

#本番では使用しない
# MEDIA_URL = "/media/"
# MEDIA_ROOT = BASE_DIR / "media"

# ==============================
# 基本設定
# ==============================

DJANGO_ENV = os.environ.get("DJANGO_ENV", "development")
DEBUG = os.environ.get("DJANGO_DEBUG") == "True"

# DEBUG = True

# DEBUG = False
# ALLOWED_HOSTS = ["*"]  # 一時的

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
    ".ngrok-free.app",
]

CSRF_TRUSTED_ORIGINS = [
    "http://127.0.0.1:8000",
    "http://localhost:8000",

    # 👇ワイルドカード
    "https://*.ngrok-free.app",
]

# blog/security.py（新規作成を推奨）

ALLOWED_VIDEO_DOMAINS = {
    "youtube.com",
    "www.youtube.com",
    "youtu.be",
    "tiktok.com",
    "www.tiktok.com",
    "lite.tiktok.com",
    "www.lite.tiktok.com",
    "line.me",
    "linevoom.line.me",
    "www.linevoom.line.me",
    "pococha.com",
    "www.pococha.com",
    "17.live",
    "www.17.live",
    "live.nicovideo.jp",
    "www.live.nicovideo.jp",
    "nico.ms",
    "whOO.ooo",
    "www.whOO.ooo",
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

SITE_URL = "https://my-python-app-0t2k.onrender.com"

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

# Stripe設定(本番では環境変数から取得することを推奨)
#本番用
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")


# =========================
# 開発環境
# =========================
if DEBUG:
    STORAGES = {
        "default": {
            "BACKEND": "cloudinary_storage.storage.MediaCloudinaryStorage",
        },
        "staticfiles": {
            "BACKEND": "whitenoise.storage.CompressedStaticFilesStorage",
        },
    }

    MEDIA_URL = "/media/"
    MEDIA_ROOT = BASE_DIR / "media"

# =========================
# 本番環境
# =========================
# きびしい設定
# else:
#     STORAGES = {
#         "default": {
#             "BACKEND": "cloudinary_storage.storage.MediaCloudinaryStorage",
#         },
#         "staticfiles": {
#             "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
#         },
#     }

# デプロイ失敗が続く場合は、少し緩い設定にする（ただしキャッシュ対策は別途必要）
else:
    STORAGES = {
        "default": {
            "BACKEND": "cloudinary_storage.storage.MediaCloudinaryStorage",
        },
        "staticfiles": {
            "BACKEND": "whitenoise.storage.CompressedStaticFilesStorage",
        },
    }

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
    # Third-party（本番で実際に使っているもの）
    "csp",
    "channels",
    "cloudinary",
    "cloudinary_storage",

    # Django core（必須）
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sitemaps",

    # Your apps（実際に存在しているアプリのみ）
    "accounts",
    "diary",
    "blog",
    "videochat",
    "user_messages",
    "notifications",
    'reels',
]

WHITENOISE_KEEP_ONLY_HASHED_FILES = True

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
    'accounts.middleware.TermsAgreementMiddleware',
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
                "accounts.context_processors.user_count",
                "accounts.context_processors.visitor_counts",
            ],
        },
    },
]

WSGI_APPLICATION = "myproject.wsgi.application"
ASGI_APPLICATION = "myproject.asgi.application"

#本番用
import os

REDIS_URL = os.environ.get("REDIS_URL")

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [REDIS_URL],
        },
    },
}

#開発用
# CHANNEL_LAYERS = {
#     "default": {
#         "BACKEND": "channels.layers.InMemoryChannelLayer",
#     },
# }

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
# メール
# ----------------------------------
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD")

DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
SERVER_EMAIL = DEFAULT_FROM_EMAIL

ADMINS = [
    ("Eden", EMAIL_HOST_USER),
]

# if DEBUG:
#     EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# ----------------------------------
# その他
# ----------------------------------
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


TEMPLATES[0]["OPTIONS"]["context_processors"] += [
    'videochat.context_processors.unclosed_room_warning',
]


# =========================
# Content Security Policy
# =========================

CONTENT_SECURITY_POLICY = {
    "DIRECTIVES": {

        "default-src": ("'self'",),

        # JavaScript
        "script-src": (
            "'self'",
            "'unsafe-inline'",
            "https://www.youtube.com",
            "https://www.youtube-nocookie.com",
            "https://www.tiktok.com",
            "https://www.instagram.com",
            "https://platform.twitter.com",
            "https://connect.facebook.net",
        ),

        # CSS
        "style-src": (
            "'self'",
            "'unsafe-inline'",
        ),

        # 画像
        "img-src": (
            "'self'",
            "data:",
            "https://res.cloudinary.com",
            "https://api.qrserver.com",
        ),

        # iframe (動画・ビデオ通話)
        "frame-src": (
            "'self'",
            "https://meet.jit.si",
            "https://www.youtube.com",
            "https://www.youtube-nocookie.com",
            "https://www.tiktok.com",
            "https://www.instagram.com",
            "https://www.facebook.com",
            "https://platform.twitter.com",
        ),

        # API / WebSocket
        "connect-src": (
            "'self'",
            "https://meet.jit.si",
            "wss://my-python-app-0t2k.onrender.com",
            "ws://127.0.0.1:8000",
            "ws://localhost:8000",
        ),

        # フォント
        "font-src": (
            "'self'",
            "data:",
        ),

        # メディア
        "media-src": (
            "'self'",
            "https://res.cloudinary.com",
        ),
    }
}

# ==========================
# キャッシュ・セッション設定（Redis / 開発用切り替え）
# ==========================
if "REDIS_URL" in os.environ:
    # 本番 Redis 用
    CACHES = {
        "default": {
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": os.environ["REDIS_URL"],
            "OPTIONS": {"CLIENT_CLASS": "django_redis.client.DefaultClient"},
        }
    }
    SESSION_ENGINE = "django.contrib.sessions.backends.cache"
    SESSION_CACHE_ALIAS = "default"
else:
    # 開発用 LocMemCache
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        }
    }
    SESSION_ENGINE = "django.contrib.sessions.backends.cache"
    SESSION_CACHE_ALIAS = "default"

# EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"