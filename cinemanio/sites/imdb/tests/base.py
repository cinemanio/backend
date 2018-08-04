from datetime import date

from cinemanio.core.tests.base import BaseTestCase
from cinemanio.sites.imdb.factories import ImdbPersonFactory


class ImdbSyncBaseTest(BaseTestCase):
    USA_ID = 69

    def imdb_dennis_hopper(self):
        return ImdbPersonFactory(id=454, person__country=None, person__first_name_en='', person__last_name_en='')

    def assert_matrix(self, imdb_movie):
        movie = imdb_movie.movie
        movie.refresh_from_db()
        imdb_movie.refresh_from_db()

        self.assertTrue(imdb_movie.synced_at)
        self.assertEqual(imdb_movie.id, 133093)
        self.assertEqual(imdb_movie.rating, 8.7)

        self.assertEqual(movie.title, 'The Matrix')
        # self.assertEqual(movie.title_ru, 'Матрица')
        self.assertEqual(movie.year, 1999)
        self.assertEqual(movie.runtime, 136)
        self.assertQuerysetEqual(movie.genres.all(), ['Action', 'Sci-Fi'])
        self.assertQuerysetEqual(movie.languages.all(), ['English'])
        self.assertQuerysetEqual(movie.countries.all(), ['USA'])
        # self.assertEqual(movie.russia_start, datetime.date(1999, 10, 14))

    def assert_matrix_cast(self, imdb_movie, person1, person2, person3):
        cast = imdb_movie.movie.cast
        self.assertEqual(person1.imdb.id, 905152)
        self.assertEqual(person2.imdb.id, 206)
        self.assertEqual(person3.imdb.id, 50390)
        self.assertEqual(cast.count(), 5)
        self.assertTrue(cast.get(person=person1, role=self.director))
        self.assertTrue(cast.get(person=person1, role=self.scenarist))
        self.assertTrue(cast.get(person=person1, role=self.producer))
        self.assertEqual(cast.get(person=person2, role=self.actor).name_en, 'Neo')
        self.assertEqual(cast.get(person=person3, role=self.actor).name_en, 'Businessman')

    def assert_dennis_hopper(self, imdb_person):
        person = imdb_person.person
        person.refresh_from_db()
        imdb_person.refresh_from_db()

        self.assertTrue(imdb_person.synced_at)
        self.assertEqual(imdb_person.id, 454)

        self.assertEqual(person.first_name, 'Dennis')
        self.assertEqual(person.last_name, 'Hopper')
        self.assertEqual(person.date_birth, date(1936, 5, 17))
        self.assertEqual(person.date_death, date(2010, 5, 29))
        self.assertEqual(person.country.id, self.USA_ID)

    def assert_dennis_hopper_career(self, imdb_person, movie1, movie2):
        career = imdb_person.person.career
        self.assertEqual(movie1.imdb.id, 64276)
        self.assertEqual(movie2.imdb.id, 108399)
        self.assertEqual(career.count(), 4)
        self.assertTrue(career.get(movie=movie1, role=self.director))
        self.assertTrue(career.get(movie=movie1, role=self.scenarist))
        self.assertEqual(career.get(movie=movie1, role=self.actor).name_en, 'Billy')
        self.assertEqual(career.get(movie=movie2, role=self.actor).name_en, 'Clifford Worley')
