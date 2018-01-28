from .settings import *

CELERY_ALWAYS_EAGER = True

TEST_RUNNER = 'djcelery.contrib.test_runner.CeleryTestSuiteRunner'
