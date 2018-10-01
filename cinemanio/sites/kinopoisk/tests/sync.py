from parameterized import parameterized
from vcr_unittest import VCRMixin

from cinemanio.core.factories import MovieFactory, PersonFactory
from cinemanio.core.models import Genre
from cinemanio.core.tests.base import BaseTestCase
from cinemanio.sites.kinopoisk.factories import KinopoiskMovieFactory, KinopoiskPersonFactory
from cinemanio.sites.kinopoisk.tests.mixins import KinopoiskSyncMixin

Person = PersonFactory._meta.model
Movie = MovieFactory._meta.model


class KinopoiskSyncTest(VCRMixin, BaseTestCase, KinopoiskSyncMixin):
    fixtures = BaseTestCase.fixtures + KinopoiskSyncMixin.fixtures

    def test_movie_matrix(self):
        kinopoisk = KinopoiskMovieFactory(
            id=301, movie__year=None, movie__title_en="", movie__genres=[], movie__countries=[]
        )
        kinopoisk.sync_details()

        self.assertEqual(kinopoisk.rating, 8.491)
        self.assertGreaterEqual(kinopoisk.votes, 321_684)
        self.assertGreater(len(kinopoisk.info), 100)

        self.assertEqual(kinopoisk.movie.title_ru, "Матрица")
        self.assertEqual(kinopoisk.movie.title_en, "The Matrix")
        self.assertEqual(kinopoisk.movie.title_original, "The Matrix")
        self.assertEqual(kinopoisk.movie.year, 1999)
        self.assertEqual(kinopoisk.movie.runtime, 136)
        self.assertQuerysetEqual(kinopoisk.movie.genres.all(), ["Action", "Sci-Fi"])
        self.assertQuerysetEqual(kinopoisk.movie.countries.all(), ["USA"])

    def test_movie_solaris(self):
        kp_movie = KinopoiskMovieFactory(id=43911, movie__title_en="")
        kp_movie.sync_details()
        self.assertEqual(kp_movie.movie.title_ru, "Солярис")
        self.assertEqual(kp_movie.movie.title_en, "")
        self.assertEqual(kp_movie.movie.title_original, "Солярис")

    def test_movie_with_genres_matrix(self):
        kinopoisk = KinopoiskMovieFactory(id=301, movie__year=None)
        kinopoisk.movie.genres.set([Genre.BLACK_AND_WHITE_ID, Genre.DOCUMENTARY_ID])
        self.assertQuerysetEqual(kinopoisk.movie.genres.all(), ["Black and white", "Documentary"])
        kinopoisk.sync_details()
        self.assertQuerysetEqual(kinopoisk.movie.genres.all(), ["Action", "Black and white", "Documentary", "Sci-Fi"])

    def test_person_johny_depp(self):
        kinopoisk = KinopoiskPersonFactory(id=6245)
        kinopoisk.sync_details()
        self.assertGreater(len(kinopoisk.info), 100)

    @parameterized.expand(
        [
            (dict(title_en="Easy Rider", year="1969"), dict(title_en="True Romance", year="1993")),
            (dict(title_ru="Беспечный ездок", year="1969"), dict(title_ru="Настоящая любовь", year="1993")),
        ]
    )
    def test_add_roles_to_person_by_movie_titles(self, movie_kwargs1, movie_kwargs2):
        movie1 = MovieFactory(**movie_kwargs1)
        movie2 = MovieFactory(**movie_kwargs2)
        kp_person = KinopoiskPersonFactory(id=9843)  # Dennis Hopper
        kp_person.sync_career()
        self.assert_dennis_hopper_career(kp_person, movie1, movie2)

    def test_add_roles_to_person_by_kinopoisk_id(self):
        kp_movie1 = KinopoiskMovieFactory(id=4220)  # Easy rider: director, Billy, writer
        kp_movie2 = KinopoiskMovieFactory(id=4149)  # True Romance: Clifford Worley
        kp_person = KinopoiskPersonFactory(id=9843)  # Dennis Hopper
        kp_person.sync_career()
        self.assert_dennis_hopper_career(kp_person, kp_movie1.movie, kp_movie2.movie)

    def test_add_posters_to_movie(self):
        kp_movie = KinopoiskMovieFactory(id=161_018)  # Les amants réguliers
        kp_movie.sync_images()
        self.assertEqual(kp_movie.movie.images.count(), 2)

        # delete one and sync again
        kp_movie.movie.images.last().image.delete()
        self.assertEqual(kp_movie.movie.images.count(), 1)
        kp_movie.sync_images()
        self.assertEqual(kp_movie.movie.images.count(), 2)

    def test_add_photos_to_person(self):
        kp_person = KinopoiskPersonFactory(id=129_095)
        kp_person.sync_images()
        self.assertEqual(kp_person.person.images.count(), 1)

    def test_sync_all_roles_of_movie(self):
        kp_movie = KinopoiskMovieFactory(id=4220)  # Easy rider
        kp_movie.sync(roles="all")
        self.assertEqual(kp_movie.movie.cast.count(), 60)
        self.assertEqual(kp_movie.movie.cast.filter(role=self.actor).count(), 49)
        self.assertEqual(kp_movie.movie.cast.filter(role=self.director).count(), 1)
        self.assertEqual(kp_movie.movie.cast.filter(role=self.producer).count(), 4)
        self.assertEqual(kp_movie.movie.cast.filter(role=self.scenarist).count(), 3)
        self.assertEqual(kp_movie.movie.cast.filter(role=self.operator).count(), 2)
        self.assertEqual(kp_movie.movie.cast.filter(role=self.editor).count(), 1)
        self.assertEqual(Person.objects.count(), 56)
        self.assertEqual(Person.objects.filter(kinopoisk=None).count(), 0)
        self.assertEqual(Person.objects.filter(first_name="").count(), 0)
        self.assertEqual(Person.objects.filter(last_name="").count(), 0)
        self.assertEqual(Person.objects.filter(first_name_en="").count(), 0)
        self.assertEqual(Person.objects.filter(last_name_en="").count(), 0)
        self.assertEqual(Person.objects.filter(first_name_ru="").count(), 0)
        self.assertEqual(Person.objects.filter(last_name_ru="").count(), 0)

        cast = kp_movie.movie.cast.get(person__kinopoisk__id=94668)
        self.assertEqual(cast.name_en, "Biker")
        self.assertEqual(cast.name_ru, "")

    def test_sync_all_roles_of_person(self):
        kp_person = KinopoiskPersonFactory(id=9843)  # Dennis Hopper
        kp_person.sync(roles="all")
        self.assertEqual(kp_person.person.career.count(), 171)
        self.assertEqual(kp_person.person.career.filter(role=self.actor).count(), 156)
        self.assertEqual(kp_person.person.career.filter(role=self.director).count(), 9)
        self.assertEqual(kp_person.person.career.filter(role=self.scenarist).count(), 5)
        self.assertEqual(kp_person.person.career.filter(role=self.editor).count(), 1)
        self.assertEqual(kp_person.person.career.filter(role=self.writer).count(), 0)
        self.assertEqual(Movie.objects.count(), 161)
        self.assertEqual(Movie.objects.filter(kinopoisk=None).count(), 0)
        self.assertEqual(Movie.objects.filter(title_en="").count(), 0)
        self.assertEqual(Movie.objects.filter(title_ru="").count(), 25)  # non-translated
        self.assertEqual(Movie.objects.filter(year=None).count(), 0)

        self.assertQuerysetEqual(Movie.objects.get(kinopoisk__id=305_858).genres.all(), ["Short"])
