import datetime
from unittest import skip

from cinemanio.core.factories import MovieFactory, PersonFactory
from cinemanio.core.tests.base import BaseTestCase
from cinemanio.sites.imdb.factories import ImdbMovieFactory, ImdbPersonFactory

USA_ID = 69


class ImdbSyncTest(BaseTestCase):
    fixtures = BaseTestCase.fixtures + [
        'imdb.imdbgenre.json',
        'imdb.imdbcountry.json',
        'imdb.imdblanguage.json',
    ]

    def assert_matrix_cast(self, imdb_movie, person1, person2, person3):
        cast = imdb_movie.movie.cast
        self.assertEqual(person1.imdb.id, 905152)
        self.assertEqual(person2.imdb.id, 206)
        self.assertEqual(person3.imdb.id, 50390)
        self.assertEqual(cast.count(), 4)
        self.assertTrue(cast.get(person=person1, role=self.director))
        self.assertTrue(cast.get(person=person1, role=self.scenarist))
        self.assertEqual(cast.get(person=person2, role=self.actor).name_en, 'Neo')
        self.assertEqual(cast.get(person=person3, role=self.actor).name_en, 'Businessman')

    def assert_dennis_hopper_career(self, imdb_person, movie1, movie2):
        career = imdb_person.person.career
        self.assertEqual(movie1.imdb.id, 64276)
        self.assertEqual(movie2.imdb.id, 108399)
        self.assertEqual(career.count(), 4)
        self.assertTrue(career.get(movie=movie1, role=self.director))
        self.assertTrue(career.get(movie=movie1, role=self.author))
        self.assertEqual(career.get(movie=movie1, role=self.actor).name_en, 'Billy')
        self.assertEqual(career.get(movie=movie2, role=self.actor).name_en, 'Clifford Worley')

    def test_get_movie_matrix(self):
        imdb_movie = ImdbMovieFactory(id=133093, movie__year=None)
        imdb_movie.sync()

        self.assertEqual(imdb_movie.movie.title, 'The Matrix')
        # self.assertEqual(imdb_movie.movie.title_ru, 'Матрица')
        self.assertEqual(imdb_movie.movie.year, 1999)
        self.assertEqual(imdb_movie.movie.runtime, 136)
        self.assertEqual(imdb_movie.movie.imdb.rating, 8.7)
        self.assertQuerysetEqual(imdb_movie.movie.genres.all(), ['Action', 'Sci-Fi'])
        self.assertQuerysetEqual(imdb_movie.movie.languages.all(), ['English'])
        self.assertQuerysetEqual(imdb_movie.movie.countries.all(), ['USA'])
        # self.assertEqual(imdb_movie.movie.russia_start, datetime.date(1999, 10, 14))

    def test_get_movie_runtime_different_format(self):
        # runtime in format "xxxxx:17"
        imdb_movie = ImdbMovieFactory(id=1524546)
        imdb_movie.sync()
        self.assertEqual(imdb_movie.movie.runtime, 17)

    def test_movie_genres_no_black_and_white_easy_rider(self):
        imdb_movie = ImdbMovieFactory(id=64276)
        imdb_movie.sync()
        self.assertQuerysetEqual(imdb_movie.movie.genres.all(), ['Adventure', 'Drama'])

    def test_movie_genres_adams_family(self):
        imdb_movie = ImdbMovieFactory(id=57729)
        imdb_movie.sync()
        self.assertQuerysetEqual(imdb_movie.movie.genres.all(), ['Black and white', 'Comedy', 'Family', 'Horror',
                                                                 'Series'])

    def test_get_person_dennis_hopper(self):
        imdb_person = ImdbPersonFactory(id=454)
        imdb_person.sync()

        self.assertEqual(imdb_person.person.first_name_en, 'Dennis')
        self.assertEqual(imdb_person.person.last_name_en, 'Hopper')
        self.assertEqual(imdb_person.person.date_birth, datetime.date(1936, 5, 17))
        self.assertEqual(imdb_person.person.date_death, datetime.date(2010, 5, 29))
        self.assertEqual(imdb_person.person.country.id, USA_ID)

    def test_add_roles_to_movie_by_imdb_id(self):
        imdb_person1 = ImdbPersonFactory(id=905152)  # director, scenarist
        imdb_person2 = ImdbPersonFactory(id=206)  # Neo
        imdb_person3 = ImdbPersonFactory(id=50390)  # other actor
        imdb_movie = ImdbMovieFactory(id=133093)
        imdb_movie.sync(roles=True)

        self.assert_matrix_cast(imdb_movie, imdb_person1.person, imdb_person2.person, imdb_person3.person)

    def test_add_roles_to_movie_by_names(self):
        person1 = PersonFactory(first_name_en='Lilly', last_name_en='Wachowski')
        person2 = PersonFactory(first_name_en='Keanu', last_name_en='Reeves')
        person3 = PersonFactory(first_name_en='Jeremy', last_name_en='Ball')
        imdb_movie = ImdbMovieFactory(id=133093)
        imdb_movie.sync(roles=True)

        self.assert_matrix_cast(imdb_movie, person1, person2, person3)

    def test_add_movies_to_writer(self):
        # writer, Dostoevskiy
        imdb_movie = ImdbMovieFactory(id=475730)
        imdb_person = ImdbPersonFactory(id=234502)
        imdb_person.sync(roles=True)

        self.assertTrue(imdb_person.person.career.filter(movie=imdb_movie.movie, role=self.author))

    def test_add_roles_to_person_by_imdb_id(self):
        imdb_movie1 = ImdbMovieFactory(id=64276)  # Easy rider: director, Billy, writer
        imdb_movie2 = ImdbMovieFactory(id=108399)  # True Romance: Clifford Worley
        imdb_person = ImdbPersonFactory(id=454)  # Dennis Hopper
        imdb_person.sync(roles=True)

        self.assert_dennis_hopper_career(imdb_person, imdb_movie1.movie, imdb_movie2.movie)

    def test_add_roles_to_person_by_movie_titles(self):
        movie1 = MovieFactory(title_en='Easy Rider', year=1969)
        movie2 = MovieFactory(title_en='True Romance', year=1993)
        imdb_person = ImdbPersonFactory(id=454)  # Dennis Hopper
        imdb_person.sync(roles=True)

        self.assert_dennis_hopper_career(imdb_person, movie1, movie2)

    @skip('notes are empty')
    def test_add_authors_to_movie(self):
        imdb_person = ImdbPersonFactory(id=234502)  # writer, Dostoevskiy
        imdb_movie = ImdbMovieFactory(id=475730)
        imdb_movie.sync(roles=True)

        self.assertTrue(imdb_movie.movie.cast.get(person=imdb_person.person, role=self.author))

    @skip('no original titles in response')
    def test_movie_title_en(self):
        imdb_movie = ImdbMovieFactory(id=190332)
        imdb_movie.sync()

        self.assertEqual(imdb_movie.movie.title, 'Wo hu cang long')
        self.assertEqual(imdb_movie.movie.title_en, 'Crouching Tiger, Hidden Dragon')
