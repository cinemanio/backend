from parameterized import parameterized
from django.test import modify_settings
from django.urls.base import reverse

from cinemanio.core.factories import MovieFactory, PersonFactory, CastFactory
from cinemanio.sites.imdb.factories import ImdbMovieFactory, ImdbPersonFactory
from cinemanio.sites.kinopoisk.factories import KinopoiskMovieFactory, KinopoiskPersonFactory
from cinemanio.images.factories import ImageLinkFactory
from cinemanio.core.tests.base import BaseTestCase
from cinemanio.users.factories import UserFactory, User


class AdminBaseTest(BaseTestCase):
    password = 'secret'

    def setUp(self):
        users = [UserFactory(username='user', is_staff=False, is_active=True, is_superuser=False),
                 UserFactory(username='user_another', is_staff=False, is_active=True, is_superuser=False),
                 UserFactory(username='moderator', is_staff=True, is_active=True, is_superuser=False),
                 UserFactory(username='admin', is_staff=True, is_active=True, is_superuser=True)]

        for user in users:
            user.set_password(self.password)
            user.save()

    def _login(self, username):
        if self.client.login(username=username, password=self.password):
            self.user = User.objects.get(username=username)
        else:
            raise ValueError('Auth error of user "%s"' % username)

    def _logout(self):
        self.client.logout()


class AdminTest(AdminBaseTest):
    def setUp(self):
        super().setUp()
        self._login('admin')

    # @modify_settings(MIDDLEWARE={'remove': 'silk.middleware.SilkyMiddleware'})
    @parameterized.expand([
        ('movie', ImdbMovieFactory, KinopoiskMovieFactory),
        ('person', ImdbPersonFactory, KinopoiskPersonFactory),
    ])
    def test_objects_page(self, object_type, imdb_factory, kinopoisk_factory):
        for i in range(100):
            kinopoisk_factory(person=getattr(imdb_factory(), object_type))

        with self.assertNumQueries(7):
            response = self.client.get(reverse(f'admin:core_{object_type}_changelist'))
        self.assertEqual(response.status_code, 200)

    @parameterized.expand([
        ('movie', MovieFactory, ImdbMovieFactory, KinopoiskMovieFactory, 17),
        ('person', PersonFactory, ImdbPersonFactory, KinopoiskPersonFactory, 12),
    ])
    def test_object_page(self, object_type, factory, imdb_factory, kinopoisk_factory, queries):
        instance = factory()
        imdb_factory(**{object_type: instance})
        kinopoisk_factory(**{object_type: instance})
        for i in range(100):
            CastFactory(**{object_type: instance})
        for i in range(10):
            ImageLinkFactory(object=instance)

        # TODO: prefetch thumbnails with one extra query
        with self.assertNumQueries(queries + 10):
            response = self.client.get(reverse(f'admin:core_{object_type}_change', args=(instance.id,)))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, f'Imdb {object_type}s')
        self.assertContains(response, f'Kinopoisk {object_type}s')
        self.assertContains(response, 'Cast')
        self.assertContains(response, 'Image links')
