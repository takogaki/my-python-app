from pathlib import Path
import os
import dj_database_url
from dotenv import load_dotenv

load_dotenv()

# ==============================
# 📁 パス設定
# ==============================
BASE_DIR = Path(__file__).resolve().parent.parent

# ==============================
# 🌍 環境設定
# ==============================
DJANGO_ENV = os.environ.get("DJANGO_ENV", "development")
DEBUG = os.environ.get("DJANGO_DEBUG") == "True"

SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "dev-secret-key-unsafe")

# ==============================
# 🌐 ホスト設定
# ==============================
ALLOWED_HOSTS = [
    "localhost",
    "127.0.0.1",
    "my-python-app-0t2k.onrender.com",
    ".onrender.com",
    ".ngrok-free.app",
]

RENDER_EXTERNAL_HOSTNAME = os.environ.get("RENDER_EXTERNAL_HOSTNAME")
if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)

RENDER_INTERNAL_HOSTNAME = os.environ.get("RENDER_INTERNAL_HOSTNAME")
if RENDER_INTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_INTERNAL_HOSTNAME)

SITE_URL = "https://my-python-app-0t2k.onrender.com"

# ==============================
# 📦 静的ファイル（最重要）
# ==============================
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

# 共通 static フォルダ
STATICFILES_DIRS = [
    BASE_DIR / "static",
]

# 開発中は finder を使う（WhiteNoiseと相性◎）
STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
]

# ==============================
# ☁️ ストレージ設定
# ==============================
# staticfiles は WhiteNoise を使う（開発・本番ともに安定重視）
STATICFILES_STORAGE = "whitenoise.storage.CompressedStaticFilesStorage"

if DEBUG:
    # 開発
    STORAGES = {
        "default": {
            "BACKEND": "cloudinary_storage.storage.MediaCloudinaryStorage",
        },
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
        },
    }
else:
    # 本番（まずは安定重視）
    STORAGES = {
        "default": {
            "BACKEND": "cloudinary_storage.storage.MediaCloudinaryStorage",
        },
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
        },
    }

# Cloudinary
CLOUDINARY_STORAGE = {
    "CLOUD_NAME": os.environ.get("CLOUDINARY_CLOUD_NAME"),
    "API_KEY": os.environ.get("CLOUDINARY_API_KEY"),
    "API_SECRET": os.environ.get("CLOUDINARY_API_SECRET"),
}

# ==============================
# 🔐 セキュリティ設定
# ==============================
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
else:
    SECURE_SSL_REDIRECT = False

    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SECURE = False

    SESSION_COOKIE_SAMESITE = "Lax"
    CSRF_COOKIE_SAMESITE = "Lax"

    CSRF_TRUSTED_ORIGINS = [
        "http://127.0.0.1:8000",
        "http://localhost:8000",
    ]

# ==============================
# 💳 Stripe
# ==============================
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")

# ==============================
# 📦 アプリ
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
    "django.contrib.sitemaps",

    "accounts",
    "diary",
    "blog",
    "videochat",
    "user_messages",
    "notifications",
    "reels",
]

# ==============================
# 🧱 ミドルウェア
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

# ==============================
# 🎨 テンプレート
# ==============================
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
                "videochat.context_processors.unclosed_room_warning",
            ],
        },
    },
]

ROOT_URLCONF = "myproject.urls"
WSGI_APPLICATION = "myproject.wsgi.application"
ASGI_APPLICATION = "myproject.asgi.application"

# ==============================
# 🗄️ DB
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
# 🔑 認証
# ==============================
AUTH_USER_MODEL = "accounts.CustomUser"

LOGIN_URL = "/accounts/login/"
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/accounts/login/"

# ==============================
# 🌍 言語・時間
# ==============================
LANGUAGE_CODE = "ja"
TIME_ZONE = "Asia/Tokyo"
USE_I18N = True
USE_TZ = True

# ==============================
# 🔌 Channels（WebSocket）
# ==============================
REDIS_URL = os.environ.get("REDIS_URL")

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [REDIS_URL],
        },
    },
}

# ==============================
# ⚡ キャッシュ・セッション
# ==============================
if REDIS_URL:
    CACHES = {
        "default": {
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": REDIS_URL,
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

# ==============================
# 📧 メール
# ==============================
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD")

DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

# ==============================
# 🛡️ CSP（セキュリティ）
# ==============================
CONTENT_SECURITY_POLICY = {
    "DIRECTIVES": {
        "default-src": ("'self'",),
        "script-src": (
            "'self'", "'unsafe-inline'",
            "https://www.youtube.com",
            "https://www.tiktok.com",
        ),
        "style-src": ("'self'", "'unsafe-inline'"),
        "img-src": (
            "'self'", "data:",
            "https://res.cloudinary.com",
        ),
    }
}

# ==============================
# 🔧 その他
# ==============================
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# WhiteNoise（開発用）
WHITENOISE_AUTOREFRESH = True
WHITENOISE_USE_FINDERS = True