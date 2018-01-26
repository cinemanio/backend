from django.test import TestCase


class BaseTestCase(TestCase):
    fixtures = [
        'core.role.json',
        'core.genre.json',
        'core.country.json',
        'core.type.json',
        'core.language.json',
    ]
