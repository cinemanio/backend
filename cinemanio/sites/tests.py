from vcr_unittest import VCRMixin

from cinemanio.core.factories import MovieFactory, PersonFactory
from cinemanio.core.tests.base import BaseTestCase
from cinemanio.sites.imdb.tests.mixins import ImdbSyncMixin
from cinemanio.sites.kinopoisk.factories import KinopoiskPersonFactory
from cinemanio.sites.kinopoisk.tests.mixins import KinopoiskSyncMixin

Person = PersonFactory._meta.model
Movie = MovieFactory._meta.model


class SitesSyncTest(VCRMixin, BaseTestCase, ImdbSyncMixin, KinopoiskSyncMixin):
    fixtures = BaseTestCase.fixtures + ImdbSyncMixin.fixtures + KinopoiskSyncMixin.fixtures

    def test_sync_all_roles_of_person_from_imdb_and_kinopoisk(self):
        imdb_person = self.imdb_dennis_hopper()
        person = imdb_person.person
        kp_person = KinopoiskPersonFactory(id=9843, person=person)

        kp_person.sync(roles='all')
        self.assertEqual(person.career.count(), 171)
        self.assertEqual(Movie.objects.count(), 161)

        self.assertEqual(Movie.objects.filter(kinopoisk=None).count(), 0)

        self.assertEqual(Movie.objects.filter(title='').count(), 0)
        self.assertEqual(Movie.objects.filter(title_en='').count(), 0)
        self.assertEqual(Movie.objects.filter(title_ru='').count(), 25)
        self.assertEqual(Movie.objects.filter(year=None).count(), 0)

        imdb_person.sync(roles='all')
        self.assertEqual(person.career.count(), 175)
        self.assertEqual(Movie.objects.count(), 164)

        self.assertEqual(Movie.objects.exclude(kinopoisk=None).exclude(imdb=None).count(), 145)
        self.assertEqual(Movie.objects.filter(imdb=None).count(), 16)
        self.assertEqual(Movie.objects.filter(kinopoisk=None).count(), 3)
        self.assertListEqual(list(Movie.objects.filter(kinopoisk=None).values_list('imdb__id', flat=True)),
                             [4854316, 474554, 2468150])

        self.assertEqual(Movie.objects.filter(title='').count(), 0)
        self.assertEqual(Movie.objects.filter(title_en='').count(), 0)
        self.assertEqual(Movie.objects.filter(title_ru='').count(), 28)
        self.assertEqual(Movie.objects.filter(year=None).count(), 0)

        movie = Movie.objects.get(imdb__id=172794)
        self.assertEqual(movie.title, 'Michael Angel')
        self.assertEqual(movie.title_ru, 'Почерк убийцы')
        # self.assertEqual(movie.title_en, 'The Apostate')  # en title from imdb
        self.assertEqual(movie.year, 1999)  # 2000 on imdb
