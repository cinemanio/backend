from parameterized import parameterized
from vcr_unittest import VCRMixin

from cinemanio.core.factories import MovieFactory
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

    @parameterized.expand([
        (dict(title_en='Easy Rider', year='1969'),
         dict(title_en='True Romance', year='1993'),),
        (dict(title_ru='Беспечный ездок', year='1969'),
         dict(title_ru='Настоящая любовь', year='1993'),),
    ])
    def test_add_roles_to_person_by_movie_titles(self, movie_kwargs1, movie_kwargs2):
        movie1 = MovieFactory(**movie_kwargs1)
        movie2 = MovieFactory(**movie_kwargs2)
        kp_person = KinopoiskPersonFactory(id=9843)  # Dennis Hopper
        kp_person.sync_details()

        self.assert_dennis_hopper_career(kp_person, movie1, movie2)

    def test_add_roles_to_person_by_kinopoisk_id(self):
        kp_movie1 = KinopoiskMovieFactory(id=4220)  # Easy rider: director, Billy, writer
        kp_movie2 = KinopoiskMovieFactory(id=4149)  # True Romance: Clifford Worley
        kp_person = KinopoiskPersonFactory(id=9843)  # Dennis Hopper
        kp_person.sync_details()

        self.assert_dennis_hopper_career(kp_person, kp_movie1.movie, kp_movie2.movie)

    def assert_dennis_hopper_career(self, kp_person, movie1, movie2):
        career = kp_person.person.career
        self.assertEqual(movie1.kinopoisk.id, 4220)
        self.assertEqual(movie2.kinopoisk.id, 4149)
        self.assertEqual(career.count(), 4)
        self.assertTrue(career.get(movie=movie1, role=self.director))
        self.assertTrue(career.get(movie=movie1, role=self.scenarist))
        self.assertEqual(career.get(movie=movie1, role=self.actor).name_en, 'Billy')
        self.assertEqual(career.get(movie=movie2, role=self.actor).name_en, 'Clifford Worley')
