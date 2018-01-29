from vcr_unittest import VCRMixin

from cinemanio.core.tests.base import BaseTestCase
from cinemanio.sites.kinopoisk.factories import KinopoiskMovieFactory, KinopoiskPersonFactory


class KinopoiskSyncTest(VCRMixin, BaseTestCase):
    def test_movie_redacted(self):
        kinopoisk = KinopoiskMovieFactory(id=278229)
        kinopoisk.sync_details()

        self.assertEqual(kinopoisk.rating, 6.120)
        self.assertGreater(len(kinopoisk.info), 100)

    def test_person_johny_depp(self):
        kinopoisk = KinopoiskPersonFactory(id=6245)
        kinopoisk.sync_details()

        self.assertGreater(len(kinopoisk.info), 100)
