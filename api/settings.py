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

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "insecure-default-key")

# SECURITY WARNING: don't run with debug turned on in production!
# DEBUG = os.getenv("DJANGO_DEBUG", "False") == "True"
DEBUG = True

# ALLOWED_HOSTS = ["*"]

# ALLOWED_HOSTS = os.getenv("DJANGO_ALLOWED_HOSTS", "89.117.37.128").split(",")

ALLOWED_HOSTS = os.getenv(
    "DJANGO_ALLOWED_HOSTS", "127.0.0.1,localhost,89.117.37.128"
).split(",")


CORS_ALLOWED_ORIGINS = [
    "http://89.117.37.128",
    "http://localhost:8000",
    "http://localhost:5173",
    "http://127.0.0.1:8000",
    "http://127.0.0.1:5173",
]
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
    # third party dependencies
    "rest_framework_simplejwt.token_blacklist",
    "drf_yasg",
    "rest_framework",
    "django_filters",
    "corsheaders",
    "rest_framework_simplejwt",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
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


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

# DATABASES = {
#     "default": {
#         "ENGINE": "django.db.backends.sqlite3",
#         "NAME": BASE_DIR / "db.sqlite3",
#     }
# }

DATABASES = DATABASES = {
    "default": dj_database_url.config(
        default=os.getenv("DATABASE_URL"),
        conn_max_age=600,
        conn_health_checks=True,
        engine="django.db.backends.postgresql",
        ssl_require=False,  # Explicitly disable SSL
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

# API NINJA
X_SECRET_KEY = os.getenv("X_SECRET_KEY")

# API KEY FOR TERMII
API_KEY = os.getenv("API_KEY")

# Doja NIN verification
DOJAH_APP_ID = os.getenv("DOJAH_APP_ID")
DOJAH_AUTHORIZATION = os.getenv("DOJAH_AUTHORIZATION")


# TWILO
OTP_TWILIO_ACCOUNT = os.getenv("OTP_TWILIO_ACCOUNT")
OTP_TWILIO_AUTH = os.getenv("OTP_TWILIO_AUTH")
VERIFY_SID = os.getenv("VERIFY_SID")
