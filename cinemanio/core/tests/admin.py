from unittest import skip

from django.db import connection
from django.test.utils import CaptureQueriesContext
from django.urls.base import reverse

from cinemanio.core.factories import MovieFactory, PersonFactory, CastFactory
from cinemanio.sites.imdb.factories import ImdbMovieFactory, ImdbPersonFactory
from cinemanio.sites.kinopoisk.factories import KinopoiskMovieFactory, KinopoiskPersonFactory
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

    def getResponseWithQueries(self, name, args=None):
        with CaptureQueriesContext(connection) as queries:
            response = self.client.get(reverse(name, args=args))
        return response, queries

    def test_movies_page(self):
        for i in range(100):
            KinopoiskMovieFactory(movie=ImdbMovieFactory().movie)

        response, queries = self.getResponseWithQueries('admin:core_movie_changelist')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(queries), 7)

    def test_persons_page(self):
        for i in range(100):
            KinopoiskPersonFactory(person=ImdbPersonFactory().person)

        response, queries = self.getResponseWithQueries('admin:core_person_changelist')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(queries), 7)

    @skip('fix request for each person in role')
    def test_movie_page(self):
        m = MovieFactory()
        ImdbMovieFactory(movie=m)
        KinopoiskMovieFactory(movie=m)
        for i in range(100):
            CastFactory(movie=m)

        response, queries = self.getResponseWithQueries('admin:core_movie_change', (m.id,))
        self.assertEqual(response.status_code, 200)
        self.assertLess(len(queries), 20)

    @skip('fix request for each movie in role')
    def test_person_page(self):
        p = PersonFactory()
        ImdbPersonFactory(person=p)
        KinopoiskPersonFactory(person=p)
        for i in range(100):
            CastFactory(person=p)

        response, queries = self.getResponseWithQueries('admin:core_person_change', (p.id,))
        self.assertEqual(response.status_code, 200)
        self.assertLess(len(queries), 20)
