import datetime
from unittest import skip, mock
from vcr_unittest import VCRMixin

from imdb.parser.http import IMDbHTTPAccessSystem
from parameterized import parameterized

from cinemanio.core.factories import MovieFactory, PersonFactory, CastFactory
from cinemanio.core.models import Genre
from cinemanio.core.tests.base import BaseTestCase
from cinemanio.sites.exceptions import PossibleDuplicate, WrongValue
from cinemanio.sites.imdb.factories import ImdbMovieFactory, ImdbPersonFactory
from cinemanio.sites.imdb.tasks import sync_movie, sync_person
from cinemanio.sites.imdb.tests.mixins import ImdbSyncMixin

Person = PersonFactory._meta.model
Movie = MovieFactory._meta.model


class ImdbSyncTest(VCRMixin, BaseTestCase, ImdbSyncMixin):
    fixtures = BaseTestCase.fixtures + ImdbSyncMixin.fixtures

    def test_sync_movie_matrix(self):
        imdb_movie = ImdbMovieFactory(id=133093, movie__year=None, movie__title='',
                                      movie__genres=[], movie__languages=[], movie__countries=[])
        sync_movie(imdb_movie.movie.id, roles=False)
        self.assert_matrix(imdb_movie)

    def test_search_and_sync_movie_matrix(self):
        movie = MovieFactory(year=1999, title='The Matrix', genres=[], languages=[], countries=[])
        sync_movie(movie.id)
        self.assert_matrix(movie.imdb)

    def test_sync_person_dennis_hopper(self):
        imdb_person = self.imdb_dennis_hopper()
        sync_person(imdb_person.person.id, roles=False)
        self.assert_dennis_hopper(imdb_person)

    def test_search_and_sync_person_dennis_hopper(self):
        person = PersonFactory(first_name_en='Dennis', last_name_en='Hopper')
        sync_person(person.id)
        self.assert_dennis_hopper(person.imdb)

    @mock.patch.object(IMDbHTTPAccessSystem, 'search_person')
    def test_search_and_sync_right_person_by_movie(self, search_person):
        person1 = PersonFactory(first_name_en='Allison', last_name_en='Williams')
        person2 = PersonFactory(first_name_en='Allison', last_name_en='Williams')
        person3 = PersonFactory(first_name_en='Allison', last_name_en='Williams')
        ImdbMovieFactory(id=1672719, movie=CastFactory(person=person1).movie)
        ImdbMovieFactory(id=2702724, movie=CastFactory(person=person2).movie)
        ImdbMovieFactory(id=1985034, movie=CastFactory(person=person3).movie)
        sync_person(person1.id)
        sync_person(person2.id)
        sync_person(person3.id)
        self.assertEqual(person1.imdb.id, 930009)
        self.assertEqual(person2.imdb.id, 8050010)
        self.assertEqual(person3.imdb.id, 4613572)
        self.assertFalse(search_person.called)

    @mock.patch.object(IMDbHTTPAccessSystem, 'search_movie')
    def test_search_and_sync_right_movie_by_person(self, search_movie):
        movie1 = MovieFactory(year=2014, title='The Prince')
        movie2 = MovieFactory(year=2014, title='The Prince')
        ImdbPersonFactory(id=2357819, person=CastFactory(movie=movie1).person)
        ImdbPersonFactory(id=3167230, person=CastFactory(movie=movie2).person)
        sync_movie(movie1.id)
        sync_movie(movie2.id)
        self.assertEqual(movie1.imdb.id, 1085492)
        self.assertEqual(movie2.imdb.id, 3505782)
        self.assertFalse(search_movie.called)

    @parameterized.expand([
        (MovieFactory, sync_movie, dict(year=2014, title='The Prince')),
        (PersonFactory, sync_person, dict(first_name_en='Allison', last_name_en='Williams')),
    ])
    def test_sync_object_duplicates(self, factory, sync_method, kwargs):
        instance1 = factory(**kwargs)
        instance2 = factory(**kwargs)
        sync_method(instance1.id)
        self.assertTrue(instance1.imdb.id)
        with self.assertRaises(PossibleDuplicate):
            sync_method(instance2.id)

    @parameterized.expand([
        ('movie', ImdbMovieFactory, dict(movie__year=2014, movie__title='The Prince')),
        ('person', ImdbPersonFactory, dict(person__first_name_en='Allison', person__last_name_en='Williams')),
    ])
    def test_sync_object_wrong_value(self, model_name, factory, kwargs):
        instance = factory(id=1, **kwargs)
        with self.assertRaises(WrongValue):
            instance.__class__.objects.create_for(getattr(instance, model_name))

    def test_get_movie_runtime_different_format(self):
        # runtime in format "xxxxx:17"
        imdb_movie = ImdbMovieFactory(id=1524546)
        imdb_movie.sync()
        self.assertEqual(imdb_movie.movie.runtime, 17)

    def test_movie_genres_no_black_and_white_easy_rider(self):
        imdb_movie = ImdbMovieFactory(id=64276, movie__genres=[])
        imdb_movie.sync()
        self.assertQuerysetEqual(imdb_movie.movie.genres.all(), ['Adventure', 'Drama'])

    def test_movie_genres_adams_family(self):
        imdb_movie = ImdbMovieFactory(id=57729, movie__genres=[])
        imdb_movie.sync()
        self.assertQuerysetEqual(imdb_movie.movie.genres.all(), ['Black and white', 'Comedy', 'Family', 'Horror',
                                                                 'Series'])

    def test_movie_exists_genres_adams_family(self):
        imdb_movie = ImdbMovieFactory(id=57729, movie__genres=[])
        imdb_movie.movie.genres.set([Genre.BLACK_AND_WHITE_ID, Genre.DOCUMENTARY_ID])
        self.assertQuerysetEqual(imdb_movie.movie.genres.all(), ['Black and white', 'Documentary'])
        imdb_movie.sync()
        self.assertQuerysetEqual(imdb_movie.movie.genres.all(), ['Black and white', 'Comedy', 'Documentary', 'Family',
                                                                 'Horror', 'Series'])

    def test_get_person_dennis_hopper(self):
        imdb_person = self.imdb_dennis_hopper()
        imdb_person.sync()

        self.assertEqual(imdb_person.person.first_name_en, 'Dennis')
        self.assertEqual(imdb_person.person.last_name_en, 'Hopper')
        self.assertEqual(imdb_person.person.date_birth, datetime.date(1936, 5, 17))
        self.assertEqual(imdb_person.person.date_death, datetime.date(2010, 5, 29))
        self.assertEqual(imdb_person.person.country.id, self.USA_ID)

    def test_add_roles_to_movie_by_imdb_id(self):
        imdb_person1 = ImdbPersonFactory(id=905152)  # Lilly Wachowski: director, scenarist, producer
        imdb_person2 = ImdbPersonFactory(id=206)  # Keanu Reeves: Neo
        imdb_person3 = ImdbPersonFactory(id=50390)  # Jeremy Ball: Businessman
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

    def test_add_imdb_id_to_persons_of_movie(self):
        imdb_movie = ImdbMovieFactory(id=133093)
        cast1 = CastFactory(movie=imdb_movie.movie, person__first_name_en='Lilly', person__last_name_en='Wachowski',
                            role=self.director)
        cast2 = CastFactory(movie=imdb_movie.movie, person__first_name_en='Keanu', person__last_name_en='Reeves',
                            role=self.actor)
        cast3 = CastFactory(movie=imdb_movie.movie, person__first_name_en='Jeremy', person__last_name_en='Ball',
                            role=self.actor)
        imdb_movie.sync(roles=True)
        self.assert_matrix_cast(imdb_movie, cast1.person, cast2.person, cast3.person)

    def test_add_movies_to_writer(self):
        # writer, Dostoevskiy
        imdb_movie = ImdbMovieFactory(id=475730)
        imdb_person = ImdbPersonFactory(id=234502, person__country=None)
        imdb_person.sync(roles=True)
        self.assertTrue(imdb_person.person.career.filter(movie=imdb_movie.movie, role=self.author))

    def test_add_roles_to_person_by_imdb_id(self):
        imdb_movie1 = ImdbMovieFactory(id=64276)  # Easy rider: director, Billy, writer
        imdb_movie2 = ImdbMovieFactory(id=108399)  # True Romance: Clifford Worley
        imdb_person = self.imdb_dennis_hopper()
        imdb_person.sync(roles=True)
        self.assert_dennis_hopper_career(imdb_person, imdb_movie1.movie, imdb_movie2.movie)

    def test_add_roles_to_person_by_movie_titles(self):
        movie1 = MovieFactory(title_en='Easy Rider', year=1969)
        movie2 = MovieFactory(title_en='True Romance', year=1993)
        imdb_person = self.imdb_dennis_hopper()
        imdb_person.sync(roles=True)
        self.assert_dennis_hopper_career(imdb_person, movie1, movie2)

    def test_add_imdb_id_to_movies_of_person(self):
        imdb_person = self.imdb_dennis_hopper()
        # TODO: fix if cast for easy rider with role actor, director will not be created
        cast1 = CastFactory(person=imdb_person.person, movie__title_en='Easy Rider', role=self.director)
        cast2 = CastFactory(person=imdb_person.person, movie__title_en='True Romance', role=self.actor)
        imdb_person.sync(roles=True)
        self.assert_dennis_hopper_career(imdb_person, cast1.movie, cast2.movie)

    def test_add_authors_to_movie(self):
        imdb_person = ImdbPersonFactory(id=234502)  # writer, Dostoevskiy
        imdb_movie = ImdbMovieFactory(id=475730)
        imdb_movie.sync(roles=True)
        self.assertTrue(imdb_movie.movie.cast.get(person=imdb_person.person, role=self.author))

    @skip('no original titles in response')
    def test_movie_title_en(self):
        imdb_movie = ImdbMovieFactory(id=190332)
        imdb_movie.sync()
        self.assertEqual(imdb_movie.movie.title_original, 'Wo hu cang long')
        self.assertEqual(imdb_movie.movie.title_en, 'Crouching Tiger, Hidden Dragon')

    def test_sync_all_roles_of_movie(self):
        imdb_movie = ImdbMovieFactory(id=64276)  # Easy rider
        imdb_movie.sync(roles='all')
        self.assertEqual(imdb_movie.movie.cast.count(), 60)
        self.assertEqual(imdb_movie.movie.cast.filter(role=self.actor).count(), 49)
        self.assertEqual(imdb_movie.movie.cast.filter(role=self.director).count(), 1)
        self.assertEqual(imdb_movie.movie.cast.filter(role=self.producer).count(), 4)
        self.assertEqual(imdb_movie.movie.cast.filter(role=self.scenarist).count(), 3)
        self.assertEqual(imdb_movie.movie.cast.filter(role=self.operator).count(), 2)
        self.assertEqual(imdb_movie.movie.cast.filter(role=self.editor).count(), 1)
        self.assertEqual(Person.objects.count(), 56)
        self.assertEqual(Person.objects.filter(imdb=None).count(), 0)
        self.assertEqual(Person.objects.filter(first_name='').count(), 0)
        self.assertEqual(Person.objects.filter(last_name='').count(), 0)
        self.assertEqual(Person.objects.filter(first_name_en='').count(), 0)
        self.assertEqual(Person.objects.filter(last_name_en='').count(), 0)

    def test_sync_all_roles_of_person(self):
        imdb_person = self.imdb_dennis_hopper()
        imdb_person.sync(roles='all')
        self.assertEqual(imdb_person.person.career.count(), 158)
        self.assertEqual(imdb_person.person.career.filter(role=self.actor).count(), 143)
        self.assertEqual(imdb_person.person.career.filter(role=self.director).count(), 9)
        self.assertEqual(imdb_person.person.career.filter(role=self.scenarist).count(), 4)
        self.assertEqual(imdb_person.person.career.filter(role=self.writer).count(), 1)
        self.assertEqual(Movie.objects.count(), 148)
        self.assertEqual(Movie.objects.filter(imdb=None).count(), 0)
        self.assertEqual(Movie.objects.filter(title='').count(), 0)
        self.assertEqual(Movie.objects.filter(title_en='').count(), 0)
        self.assertEqual(Movie.objects.filter(year=None).count(), 0)
