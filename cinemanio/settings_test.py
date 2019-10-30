from os.path import join
import logging

from cinemanio.settings import *  # noqa

logging.disable(logging.CRITICAL)

CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True

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
