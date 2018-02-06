from .settings import *

CELERY_ALWAYS_EAGER = True

TEST_RUNNER = 'djcelery.contrib.test_runner.CeleryTestSuiteRunner'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}
