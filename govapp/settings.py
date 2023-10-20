"""Django settings for the Prescribed Burns System project.

Generated by `django-admin startproject` using Django 3.2.16.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""

import json
import os
import pathlib
import platform
from typing import Any

import decouple
import dj_database_url
import django_stubs_ext
import sentry_sdk

django_stubs_ext.monkeypatch()

ENABLE_SENTRY = decouple.config("ENABLE_SENTRY", default=False, cast=bool)
if ENABLE_SENTRY:
    sentry_sdk.init(
        dsn="https://2821da8164c0ca4d252b6ab70f605e41@sentry-uat.dbca.wa.gov.au/3",
        # Set traces_sample_rate to 1.0 to capture 100%
        # of transactions for performance monitoring.
        traces_sample_rate=1.0,
    )

# Build paths inside the project like this: BASE_DIR / "subdir".
BASE_DIR = pathlib.Path(__file__).resolve().parent.parent
STATIC_ROOT = BASE_DIR / "staticfiles"

# Project specific settings
PROJECT_TITLE = "Bushfire Mitigation System"
PROJECT_DESCRIPTION = (
    "A system to manage risk, planning, implementation and post-implementation "
    "review for the mitigation of bushfires in Western Australia"
)
PROJECT_VERSION = "v2"

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/
# SECURITY WARNING: keep the secret key used in production secret!
# SECURITY WARNING: don't run with debug turned on in production!
# SECURITY WARNING: don't allow all hosts in production!
SECRET_KEY = decouple.config("SECRET_KEY")
DEBUG = decouple.config("DEBUG", default=False, cast=bool)
ALLOWED_HOSTS = [""]
if DEBUG is True:
    ALLOWED_HOSTS = ["*"]
    CSRF_TRUSTED_ORIGINS = ["https://*.dbca.wa.gov.au"]
else:
    ALLOWED_HOSTS_STRING = decouple.config("ALLOWED_HOSTS", default='[""]')
    CSRF_TRUSTED_ORIGINS = decouple.config("CSRF_TRUSTED_ORIGINS", default='[""]')
    ALLOWED_HOSTS = json.loads(ALLOWED_HOSTS_STRING)


# Application definition
INSTALLED_APPS = [
    "reversion",
    "django.contrib.auth",
    "django.contrib.admin",
    "django.contrib.contenttypes",
    "django.contrib.gis",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "corsheaders",
    "webtemplate_dbca",
    "govapp",
    "govapp.apps.accounts",
    "govapp.apps.aviation",
    "govapp.apps.burnplanning",
    "govapp.apps.swagger",
    "govapp.apps.main",
    "rest_framework",
    "drf_spectacular",
    "django_filters",
    "django_cron",
    "django_extensions",
    "coverage",
    "protected_media.apps.ProtectedMediaConfig",
]
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "dbca_utils.middleware.SSOLoginMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "govapp.middleware.CacheControl",
]
ROOT_URLCONF = "govapp.urls"
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            BASE_DIR / "govapp/templates",
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "govapp.context_processors.variables",
            ],
        },
    },
]
WSGI_APPLICATION = "govapp.wsgi.application"

# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases
DATABASES = {
    "default": decouple.config(
        "DATABASE_URL", cast=dj_database_url.parse, default="sqlite://memory"
    ),
    "test": decouple.config(
        "TEST_DATABASE_URL", cast=dj_database_url.parse, default="sqlite://memory"
    ),
}

# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/
LANGUAGE_CODE = "en-au"
# TIME_ZONE = "UTC"
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/
STATIC_URL = "/static/"
STATICFILES_DIRS = [
    os.path.join(os.path.join(BASE_DIR, "govapp", "static")),
]

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Caching settings
# https://docs.djangoproject.com/en/3.2/ref/settings/#caches
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.filebased.FileBasedCache",
        "LOCATION": BASE_DIR / "govapp/cache",
        "OPTIONS": {"MAX_ENTRIES": 10000},
    }
}

# DBCA Template Settings
# https://github.com/dbca-wa/django-base-template/blob/main/govapp/settings.py
DEV_APP_BUILD_URL = decouple.config("DEV_APP_BUILD_URL", default=None)
ENABLE_DJANGO_LOGIN = decouple.config("ENABLE_DJANGO_LOGIN", default=False, cast=bool)
LEDGER_TEMPLATE = "bootstrap5"
GIT_COMMIT_HASH = os.popen(
    f"cd {BASE_DIR}; git log -1 --format=%H"
).read()  # noqa: S605
GIT_COMMIT_DATE = os.popen(
    f"cd {BASE_DIR}; git log -1 --format=%cd"
).read()  # noqa: S605
VERSION_NO = "2.00"

# Django REST Framework Settings
# https://www.django-rest-framework.org/api-guide/settings/
REST_FRAMEWORK = {
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
    ],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.LimitOffsetPagination",
    "PAGE_SIZE": 100,
}

# DRF Spectacular Settings
# https://drf-spectacular.readthedocs.io/en/latest/settings.html
SPECTACULAR_SETTINGS = {
    "TITLE": PROJECT_TITLE,
    "DESCRIPTION": PROJECT_DESCRIPTION,
    "VERSION": PROJECT_VERSION,
    "SERVE_INCLUDE_SCHEMA": True,
    "POSTPROCESSING_HOOKS": [],
    "COMPONENT_SPLIT_REQUEST": True,
}

# Logging
# https://docs.djangoproject.com/en/3.2/topics/logging/
LOGGING: dict[str, Any] = {
    "version": 1,
    "disable_existing_loggers": True,
    "formatters": {
        "verbose": {
            "format": "%(levelname)s %(asctime)s %(name)s [Line:%(lineno)s][%(funcName)s] %(message)s"
        },
        "simple": {"format": "%(levelname)s %(message)s"},
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "DEBUG",
            "formatter": "verbose",
        },
        "console_simple": {
            "class": "logging.StreamHandler",
            "level": "DEBUG",
            "formatter": "simple",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
    "loggers": {
        "govapp": {
            "handlers": ["console"],
            "level": "INFO",
        },
    },
}

if DEBUG is True:
    LOGGING["loggers"]["govapp"]["handlers"] = ["console_simple"]
    LOGGING["loggers"]["govapp"]["level"] = "DEBUG"
    LOGGING["loggers"]["govapp"]["propagate"] = False


# Email
DISABLE_EMAIL = decouple.config("DISABLE_EMAIL", default=False, cast=bool)
# EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_BACKEND = "wagov_utils.components.utils.email_backend.EmailBackend"
EMAIL_HOST = decouple.config("EMAIL_HOST", default="smtp.lan.fyi")
EMAIL_PORT = decouple.config("EMAIL_PORT", default=25, cast=int)
DEFAULT_FROM_EMAIL = "no-reply@dbca.wa.gov.au"
EMAIL_INSTANCE = decouple.config("EMAIL_INSTANCE", default="PROD")
NON_PROD_EMAIL = decouple.config("NON_PROD_EMAIL", default="")
PRODUCTION_EMAIL = decouple.config("PRODUCTION_EMAIL", default=False, cast=bool)
EMAIL_DELIVERY = decouple.config("EMAIL_DELIVERY", default="off")

# Cron Jobs
# https://django-cron.readthedocs.io/en/latest/installation.html
# https://django-cron.readthedocs.io/en/latest/configuration.html
# CRON_SCANNER_CLASS = "govapp.apps.catalogue.cron.ScannerCronJob"
CRON_SCANNER_PERIOD_MINS = 3  # Run every 5 minutes
CRON_CLASSES: list[str] = []


# Temporary Fix for ARM Architecture
if platform.machine() == "arm64":
    GDAL_LIBRARY_PATH = "/opt/homebrew/opt/gdal/lib/libgdal.dylib"
    GEOS_LIBRARY_PATH = "/opt/homebrew/opt/geos/lib/libgeos_c.dylib"


# Django Timezone
TIME_ZONE = "Australia/Perth"

# Protected Media
PROTECTED_MEDIA_ROOT = "%s/protected/" % BASE_DIR
PROTECTED_MEDIA_URL = "/protected"
if DEBUG is False:
    PROTECTED_MEDIA_SERVER = "nginx"  # Defaults to "django"
PROTECTED_MEDIA_LOCATION_PREFIX = "/internal"  # Prefix used in nginx config
PROTECTED_MEDIA_AS_DOWNLOADS = (
    False  # Controls inclusion of a Content-Disposition header
)

# Todo do we need this?
AZURE_OUTPUT_SYNC_DIRECTORY = ""

SEASON_CHOICES = (
    ("autumn", "Autumn"),
    ("winter", "Winter"),
    ("spring", "Spring"),
    ("summer", "Summer"),
)

# Groups

CORPORATE_EXECUTIVE = "Corporate Executive"
DISTRICT_DUTY_OFFICER = "District Duty Officer"
DISTRICT_FIRE_COORDINATOR = "District Fire Coordinator"
DISTRICT_MANAGER = "District Manager"
DJANGO_ADMIN = "Django Admin"
FMSB_REPRESENTATIVE = "FMSB Representative"
OFFICER = "Officer"
REGIONAL_DUTY_OFFICER = "Regional Duty Officer"
REGIONAL_LEADER_FIRE = "Regional Leader Fire"
REGIONAL_MANAGER = "Regional Manager"
SCHEDULER = "Scheduler"
STATE_AVIATION = "State Aviation"
STATE_DUTY_OFFICER = "State Duty Officer"
STATE_MANAGER = "State Manager"

DJANGO_GROUPS = [
    CORPORATE_EXECUTIVE,
    DISTRICT_DUTY_OFFICER,
    DISTRICT_FIRE_COORDINATOR,
    DISTRICT_MANAGER,
    DJANGO_ADMIN,
    FMSB_REPRESENTATIVE,
    OFFICER,
    REGIONAL_DUTY_OFFICER,
    REGIONAL_LEADER_FIRE,
    REGIONAL_MANAGER,
    SCHEDULER,
    STATE_AVIATION,
    STATE_DUTY_OFFICER,
    STATE_MANAGER,
]
