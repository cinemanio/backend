from vcr_unittest import VCRMixin as VCRMixinBase

from django.test import TestCase
from django.utils import translation

from cinemanio.core.models import Role


class BaseTestCase(TestCase):
    fixtures = [
        'core.role.json',
        'core.genre.json',
        'core.country.json',
        'core.language.json',
    ]

    def setUp(self):
        translation.activate('en')
        super().setUp()

    @property
    def actor(self):
        return Role.objects.get_actor()

    @property
    def director(self):
        return Role.objects.get_director()

    @property
    def producer(self):
        return Role.objects.get_producer()

    @property
    def author(self):
        return Role.objects.get_author()

    @property
    def scenarist(self):
        return Role.objects.get_scenarist()


class VCRMixin(VCRMixinBase):
    def _get_vcr_kwargs(self, **kwargs):
        kwargs['record_mode'] = 'new_episodes'
        return kwargs
