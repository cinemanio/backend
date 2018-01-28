from django.test import TestCase
from django.utils import translation


class BaseTestCase(TestCase):
    fixtures = [
        'core.role.json',
        'core.genre.json',
        'core.country.json',
        'core.type.json',
        'core.language.json',
    ]

    def setUp(self):
        translation.activate('en')
        super(BaseTestCase, self).setUp()
