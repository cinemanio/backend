"""
Django settings for cinemanio project.

Generated by 'django-admin startproject' using Django 2.0.1.

For more information on this file, see
https://docs.djangoproject.com/en/2.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.0/ref/settings/
"""
import dj_database_url
import os
from datetime import timedelta
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
    'modeltranslation',  # before admin for integration
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # third party apps
    'django_extensions',
    'debug_toolbar',
    'reversion',
    'djcelery',
    'celerymon',
    'corsheaders',
    'graphene_django',
    'silk',
    'sorl.thumbnail',
    'storages',

    # cinemanio apps
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
        conn_max_age=500,
        default=config('DATABASE_URL', default='sqlite:///{}'.format(os.path.join(BASE_DIR, 'db.sqlite3'))))
}


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

STATICFILES_STORAGE = 'whitenoise.django.GzipManifestStaticFilesStorage'

# Amazon S3
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
AWS_S3_REGION_NAME = 'us-east-2'
AWS_S3_SIGNATURE_VERSION = 's3v4'
AWS_ACCESS_KEY_ID = config('AWS_ACCESS_KEY_ID', default='')
AWS_SECRET_ACCESS_KEY = config('AWS_SECRET_ACCESS_KEY', default='')
AWS_STORAGE_BUCKET_NAME = config('AWS_STORAGE_BUCKET_NAME', default='cinemanio')

# celery
CELERY_HOST = '127.0.0.1'
BROKER_URL = 'amqp://user:pass@%s:5672/name' % CELERY_HOST
CELERY_SEND_TASK_ERROR_EMAILS = True
CELERY_TASK_RESULT_EXPIRES = None
CELERY_ACKS_LATE = True
CELERYD_CONCURRENCY = 3
CELERY_RESULT_BACKEND = 'djcelery.backends.database:DatabaseBackend'
CELERYBEAT_SCHEDULER = 'djcelery.schedulers.DatabaseScheduler'
CELERYCAM_EXPIRE_SUCCESS = timedelta(days=5)
CELERYCAM_EXPIRE_ERROR = timedelta(days=10)
CELERYCAM_EXPIRE_PENDING = timedelta(days=10)

SENTRY_DSN = config('SENTRY_DSN', default='')
RAVEN_CONFIG = {
    'dsn': SENTRY_DSN,
    'release': '0.3.6',
}

GRAPHENE = {
    'SCHEMA': 'cinemanio.schema.schema',
    'MIDDLEWARE': ['graphene_django.debug.DjangoDebugMiddleware'] if DEBUG else [],
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
