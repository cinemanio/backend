from vcr_unittest import VCRMixin

from cinemanio.core.tests.base import BaseTestCase
from cinemanio.core.factories import MovieFactory
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

    # TODO: implement
    # def test_add_roles_to_person_by_kinopoisk_id(self):
    #     kp_movie1 = KinopoiskMovieFactory(id=4220)  # Easy rider: director, Billy, writer
    #     kp_movie2 = KinopoiskMovieFactory(id=4149)  # True Romance: Clifford Worley
    #     kp_person = KinopoiskPersonFactory(id=9843)  # Dennis Hopper
    #     kp_person.sync_career()
    #
    #     career = kp_person.person.career
    #     self.assertEqual(career.count(), 4)
    #     self.assertTrue(career.get(movie=kp_movie1.movie, role=self.director))
    #     self.assertTrue(career.get(movie=kp_movie1.movie, role=self.author))
    #     self.assertEqual(career.get(movie=kp_movie1.movie, role=self.actor).name_en, 'Billy')
    #     self.assertEqual(career.get(movie=kp_movie2.movie, role=self.actor).name_en, 'Clifford Worley')
    #
    # def test_add_roles_to_person_by_movie_titles(self):
    #     movie1 = MovieFactory(title_en='Easy Rider', title_ru='Беспечный ездок', year='1969')
    #     movie2 = MovieFactory(title_en='True Romance', title_ru='Настоящая любовь', year='1993')
    #     kp_person = KinopoiskPersonFactory(id=9843)  # Dennis Hopper
    #     kp_person.sync_career()
    #
    #     career = kp_person.person.career
    #     self.assertEqual(movie1.kinopoisk.id, 4220)
    #     self.assertEqual(movie2.kinopoisk.id, 4149)
    #     self.assertEqual(career.objects.count(), 4)
    #     self.assertEqual(career.get(movie=movie1, role=self.actor).name_en, 'Billy')
    #     self.assertEqual(career.get(movie=movie2, role=self.actor).name_en, 'Clifford Worley')
