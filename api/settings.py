from pathlib import Path
import dj_database_url
from dotenv import load_dotenv
import os
from datetime import timedelta
from decouple import config
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env
import environ

env = environ.Env()

environ.Env.read_env()

load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY")

DEBUG = env.bool("DJANGO_DEBUG", default=False)

# DEBUG = True


ALLOWED_HOSTS = [
    host.strip()
    for host in os.getenv("DJANGO_ALLOWED_HOSTS", "").split(",")
    if host.strip()
]

# load_dotenv(override=True)

CORS_ALLOWED_ORIGINS = [
    "https://cvms-api.afripointdev.com",
    "https://www.cvms-api.afripointdev.com",
    "http://cvms.afripointdev.com",
    "https://cvms-site.vercel.app",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]


SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
CORS_ALLOW_CREDENTIALS = True

# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # apps
    "accounts",
    "departments",
    "verifications",
    "vins_search",
    "trackers",
    "accredify",
    "api_keys",
    "payments",
    "products",
    # third party dependencies
    "rest_framework_simplejwt.token_blacklist",
    "drf_yasg",
    "rest_framework",
    "django_filters",
    "corsheaders",
    "rest_framework_simplejwt",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "api.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "api.wsgi.application"

DATABASES = {
    "default": dj_database_url.config(
        default=os.getenv("DATABASE_URL"),
        conn_max_age=600,
        conn_health_checks=True,
        ssl_require=True,
    )
}


LANGUAGE_CODE = "en-us"

TIME_ZONE = "Africa/Lagos"

USE_I18N = True

USE_TZ = True

STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"),
]

MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")
# Auth settings
AUTH_USER_MODEL = "accounts.CustomUser"

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(hours=1),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
    "SIGNING_KEY": SECRET_KEY,
    "AUTH_HEADER_TYPES": ("Bearer",),
    "BLACKLIST_AFTER_ROTATION": True,
    "ROTATE_REFRESH_TOKENS": True,
}


# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Default primary key field type
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Email settings
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = os.getenv("EMAIL_HOST")
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")
DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL")
EMAIL_PORT = os.getenv("EMAIL_PORT")

# print(EMAIL_HOST)
# print(DEFAULT_FROM_EMAIL)
# print(EMAIL_HOST_PASSWORD)


# API NINJA
API_NINJA_KEY = os.getenv("API_NINJA_KEY")

# API KEY FOR TERMII
API_KEY = os.getenv("API_KEY")

# Doja NIN verification
DOJAH_APP_ID = os.getenv("DOJAH_APP_ID")
DOJAH_AUTHORIZATION = os.getenv("DOJAH_AUTHORIZATION")


# TWILO
OTP_TWILIO_ACCOUNT = os.getenv("OTP_TWILIO_ACCOUNT")
OTP_TWILIO_AUTH = os.getenv("OTP_TWILIO_AUTH")
VERIFY_SID = os.getenv("VERIFY_SID")


STORAGES = {
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"
    },
}

SWAGGER_SETTINGS = {
    "DEFAULT_API_URL": "https://cvms-api.afripointdev.com",
    "SECURE_SCHEMA": True,
}
