from os.path import join

from cinemanio.settings import *  # noqa

CELERY_TASK_ALWAYS_EAGER = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': join(BASE_DIR, 'db.sqlite3'),
    }
}

DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'loggers': {},
}

ALGOLIA = {
    'APPLICATION_ID': '',
    'API_KEY': '',
    'AUTO_INDEXING': False,
}

EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
EMAIL_FILE_PATH = join(BASE_DIR, 'tmp/emails')
