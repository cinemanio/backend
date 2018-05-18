from os.path import join

from cinemanio.settings import *  # noqa

CELERY_ALWAYS_EAGER = True

TEST_RUNNER = 'djcelery.contrib.test_runner.CeleryTestSuiteRunner'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': join(BASE_DIR, 'db.sqlite3'),
    }
}

DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'
