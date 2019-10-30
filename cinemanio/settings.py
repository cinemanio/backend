"""
Django settings for cinemanio project.

Generated by 'django-admin startproject' using Django 2.0.1.

For more information on this file, see
https://docs.djangoproject.com/en/2.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.0/ref/settings/
"""
import os
from datetime import timedelta

import dj_database_url
from decouple import config, Csv

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('DJANGO_SECRET_KEY', default='u25$s4f_6r-#4p*be3xe6(c+8i82x)$dm+^ni36)@yy_27yy(0')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DJANGO_DEBUG', default=False, cast=bool)
ALLOWED_HOSTS = config('DJANGO_ALLOWED_HOSTS', default='.cineman.io', cast=Csv())
INTERNAL_IPS = ['127.0.0.1']

# Application definition
INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # third party apps
    'django_extensions',
    'django_cleanup',
    'django_celery_results',
    'django_celery_beat',
    'debug_toolbar',
    'reversion',
    # 'celerymon',
    'corsheaders',
    'graphene_django',
    'algoliasearch_django',
    'silk',
    'sorl.thumbnail',
    'storages',
    'anymail',
    'modeltranslation',  # before admin for integration

    # cinemanio apps
    'cinemanio.core.apps.AdminConfig',
    'cinemanio.core',
    'cinemanio.users',
    'cinemanio.relations',
    'cinemanio.api',
    'cinemanio.sites',
    'cinemanio.sites.imdb',
    'cinemanio.sites.kinopoisk',
    'cinemanio.sites.wikipedia',
    'cinemanio.images',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    # 'silk.middleware.SilkyMiddleware',
]

ROOT_URLCONF = 'cinemanio.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'cinemanio.wsgi.application'

# Database
# https://docs.djangoproject.com/en/2.0/ref/settings/#databases
DATABASES = {
    'default': dj_database_url.config(
        # conn_max_age=600,
        ssl_require=True,
        default=config('DATABASE_URL', default='sqlite:///{}'.format(os.path.join(BASE_DIR, 'db.sqlite3'))))
}

AUTHENTICATION_BACKENDS = [
    'graphql_jwt.backends.JSONWebTokenBackend',
    'django.contrib.auth.backends.ModelBackend',
]

AUTH_USER_MODEL = 'users.User'

# Password validation
# https://docs.djangoproject.com/en/2.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/2.0/topics/i18n/

gettext = lambda s: s  # noqa
LANGUAGES = (
    ('en', gettext('English')),
    ('ru', gettext('Russian')),
)

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.0/howto/static-files/
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
STATIC_URL = '/static/'

# Extra places for collectstatic to find static files.
STATICFILES_DIRS = ()

# Simplified static file serving.
# https://warehouse.python.org/project/whitenoise/

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Amazon S3
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
AWS_S3_REGION_NAME = 'us-east-2'
AWS_S3_SIGNATURE_VERSION = 's3v4'
AWS_ACCESS_KEY_ID = config('AWS_ACCESS_KEY_ID', default='')
AWS_SECRET_ACCESS_KEY = config('AWS_SECRET_ACCESS_KEY', default='')
AWS_STORAGE_BUCKET_NAME = config('AWS_STORAGE_BUCKET_NAME', default='cinemanio')

# redis
REDIS_URL = config('REDIS_URL', default='')

# celery
CELERY_BROKER_URL = REDIS_URL
CELERY_SEND_TASK_ERROR_EMAILS = True
CELERY_TASK_RESULT_EXPIRES = None
CELERY_ACKS_LATE = True
CELERYD_CONCURRENCY = 3
CELERY_RESULT_BACKEND = 'django-db'
# CELERYBEAT_SCHEDULER = 'djcelery.schedulers.DatabaseScheduler'
CELERYCAM_EXPIRE_SUCCESS = timedelta(days=5)
CELERYCAM_EXPIRE_ERROR = timedelta(days=10)
CELERYCAM_EXPIRE_PENDING = timedelta(days=10)

SENTRY_DSN = config('SENTRY_DSN', default='')
RAVEN_CONFIG = {
    'dsn': SENTRY_DSN,
    'release': '0.3.6',
}

# graphene
GRAPHENE_MIDDLEWARE = ['graphql_jwt.middleware.JSONWebTokenMiddleware']
if DEBUG:
    GRAPHENE_MIDDLEWARE += ['graphene_django.debug.DjangoDebugMiddleware']

GRAPHENE = {
    'SCHEMA': 'cinemanio.schema.schema',
    'MIDDLEWARE': GRAPHENE_MIDDLEWARE,
}

# TODO: choose right settings for CORS
CORS_ORIGIN_ALLOW_ALL = True
CORS_ORIGIN_WHITELIST = config('DJANGO_CORS_ORIGIN_WHITELIST', default='.cineman.io', cast=Csv())
CORS_URLS_REGEX = r'^/graphql/.*$'
CORS_ALLOW_METHODS = (
    'GET',
    'OPTIONS',
    'POST',
)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'cinemanio': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}

FRONTEND_URL = config('FRONTEND_URL', default='http://localhost:3000/', cast=str)

# algolia search
ALGOLIA = {
    'APPLICATION_ID': config('ALGOLIASEARCH_APPLICATION_ID', default='', cast=str),
    'API_KEY': config('ALGOLIASEARCH_API_KEY', default='', cast=str),
}

# registration
ACCOUNT_ACTIVATION_DAYS = config('ACCOUNT_ACTIVATION_DAYS', default=7, cast=int)
REGISTRATION_SALT = config('REGISTRATION_SALT', default='graphql_registration', cast=str)
PASSWORD_RESET_URL_TEMPLATE = FRONTEND_URL + 'password/reset/{uid}/{token}'
ACTIVATE_USER_URL_TEMPLATE = FRONTEND_URL + 'account/activate/{key}'

# email
ANYMAIL = {
    'MAILGUN_API_KEY': config('MAILGUN_API_KEY', default='', cast=str),
    "MAILGUN_SENDER_DOMAIN": config('MAILGUN_DOMAIN', default='', cast=str),
    'MAILGUN_SMTP_LOGIN': config('MAILGUN_SMTP_LOGIN', default='', cast=str),
    'MAILGUN_SMTP_PASSWORD': config('MAILGUN_SMTP_PASSWORD', default='', cast=str),
    'MAILGUN_SMTP_PORT': config('MAILGUN_SMTP_PORT', default='', cast=str),
    'MAILGUN_SMTP_SERVER': config('MAILGUN_SMTP_SERVER', default='', cast=str),
}
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='staff@' + ANYMAIL['MAILGUN_SENDER_DOMAIN'], cast=str)
SERVER_EMAIL = config('SERVER_EMAIL', default='server@' + ANYMAIL['MAILGUN_SENDER_DOMAIN'], cast=str)
EMAIL_BACKEND = "anymail.backends.mailgun.EmailBackend"
