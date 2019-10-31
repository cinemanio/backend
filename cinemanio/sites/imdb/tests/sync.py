import datetime
from unittest import skip, mock

from freezegun import freeze_time
from vcr_unittest import VCRMixin
from django.utils import timezone
from imdb.parser.http import IMDbHTTPAccessSystem
from parameterized import parameterized

from cinemanio.core.factories import MovieFactory, PersonFactory, CastFactory
from cinemanio.core.models import Genre
from cinemanio.core.tests.base import BaseTestCase
from cinemanio.sites.exceptions import PossibleDuplicate, WrongValue, NothingFound
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
        movie = MovieFactory(year=1999, title_en='The Matrix', genres=[], languages=[], countries=[])
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

    def test_sync_movie_series_episode(self):
        imdb_movie = ImdbMovieFactory(id=9236792)
        sync_movie(imdb_movie.movie.id, roles=False)
        with self.assertRaises(ImdbMovieFactory._meta.model.DoesNotExist):
            imdb_movie.refresh_from_db()

    @skip('https://github.com/alberanid/imdbpy/issues/242')
    def test_sync_person_with_2_ids(self):
        imdb_person = ImdbPersonFactory(id=1890852, person__country=None,
                                        person__first_name_en='', person__last_name_en='')
        sync_person(imdb_person.person.id, roles=False)
        self.assertEqual(imdb_person.id, 440022)

    def test_sync_movie_with_wrong_person(self):
        dan_brown_wrong = ImdbPersonFactory(id=1640149, person__country=None,
                                            person__first_name_en='Dan', person__last_name_en='Brown')
        imdb_movie = ImdbMovieFactory(id=382625,
                                      movie=CastFactory(person=dan_brown_wrong.person, role=self.producer).movie)
        sync_movie(imdb_movie.movie.id, roles='all')
        self.assertTrue(imdb_movie.movie.cast.get(role=self.producer, person__imdb__id=1467010))

    def test_sync_person_movies_with_the_same_title(self):
        # person has 2 movies "The Conversation" 1974 and 1995
        movie1 = MovieFactory(title_en='The Conversation', year=1974)
        imdb_person = ImdbPersonFactory(id=338)
        CastFactory(movie=movie1, person=imdb_person.person, role=self.producer)
        sync_person(imdb_person.person.id, roles='all')
        self.assertTrue(imdb_person.person.career.get(role=self.producer, movie=movie1, movie__imdb__id=71360))
        self.assertTrue(imdb_person.person.career.get(role=self.producer, movie__imdb__id=8041860))

    def test_sync_person_with_no_filmography(self):
        imdb_person = ImdbPersonFactory(id=1404411)
        sync_person(imdb_person.person.id, roles='all')
        self.assertEqual(imdb_person.person.career.count(), 0)

    @parameterized.expand([
        (ImdbPersonFactory, 1621579, sync_person, 'person'),
        (ImdbMovieFactory, 0, sync_movie, 'movie'),
    ])
    def test_sync_object_unexisted(self, imdb_factory, imdb_id, sync_method, field_name):
        imdb_object = imdb_factory(id=imdb_id)
        instance = getattr(imdb_object, field_name)
        sync_method(instance.id, roles=False)
        with self.assertRaises(imdb_factory._meta.model.DoesNotExist):
            imdb_object.refresh_from_db()

    @parameterized.expand([
        (PersonFactory, dict(first_name_en='Dan', last_name_en='Brown'), ImdbMovieFactory, dict(id=382625),
         sync_movie, 'movie', 'cast', 1467010),
        (MovieFactory, dict(title_en='Besy', year=1992), ImdbPersonFactory, dict(id=307628),
         sync_person, 'person', 'career', 103799),
    ])
    def test_sync_object_with_duplicated_cast_objects(self, factory, factory_kwargs,
                                                      imdb_factory, imdb_kwargs, sync_method,
                                                      field_name, roles_field, imdb_id):
        instance1 = factory(**factory_kwargs)
        instance2 = factory(**factory_kwargs)
        imdb_object = imdb_factory(**imdb_kwargs)
        instance = getattr(imdb_object, field_name)
        roles = getattr(instance, roles_field)
        instance_type = factory._meta.model.__name__.lower()
        cast_kwargs = {field_name: instance, 'role': self.actor, instance_type: instance1}
        CastFactory(**cast_kwargs)
        cast_kwargs[instance_type] = instance2
        CastFactory(**cast_kwargs)
        sync_method(instance.id, roles='all')
        get_kwargs = {'role': self.actor, instance_type: instance1, f'{instance_type}__imdb__id': imdb_id}
        self.assertTrue(roles.get(**get_kwargs))

    @parameterized.expand([
        (ImdbMovieFactory, dict(id=382625), sync_movie, 'movie', 'cast', dict(person__first_name_en='Dan',
                                                                              person__last_name_en='Brown')),
        (ImdbPersonFactory, dict(id=454), sync_person, 'person', 'career', dict(movie__title_en='Easy Rider',
                                                                                movie__year=1969)),
    ])
    def test_sync_object_update_cast_sources_dates(self, imdb_factory, imdb_kwargs, sync_method,
                                                   field_name, roles_field, cast_kwargs):
        now = timezone.now()
        before = now - datetime.timedelta(days=9)
        imdb_object = imdb_factory(**imdb_kwargs)
        instance = getattr(imdb_object, field_name)
        roles = getattr(instance, roles_field)
        cast_kwargs.update(**{field_name: instance})
        # created old cast
        with freeze_time(before):
            cast_old = CastFactory(role=self.actor, **cast_kwargs)
        self.assertEqual(cast_old.created_at, before)
        self.assertEqual(cast_old.updated_at, before)
        self.assertEqual(roles.count(), 1)
        with freeze_time(now):
            sync_method(instance.id, roles='all')
        self.assertGreater(roles.count(), 1)
        for cast in roles.all():
            self.assertEqual(cast.sources, 'imdb')
            self.assertEqual(cast.updated_at, now)
            self.assertEqual(cast.created_at, before if cast == cast_old else now)

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
        movie1 = MovieFactory(year=2014, title_en='The Prince')
        movie2 = MovieFactory(year=2014, title_en='The Prince')
        ImdbPersonFactory(id=2357819, person=CastFactory(movie=movie1).person)
        ImdbPersonFactory(id=3167230, person=CastFactory(movie=movie2).person)
        sync_movie(movie1.id)
        sync_movie(movie2.id)
        self.assertEqual(movie1.imdb.id, 1085492)
        self.assertEqual(movie2.imdb.id, 3505782)
        self.assertFalse(search_movie.called)

    @parameterized.expand([
        (MovieFactory, sync_movie, dict(year=2014, title_en='The Prince')),
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
        (MovieFactory, sync_movie, dict(title_en='Platina')),  # no year in search results
    ])
    def test_sync_object_nothing_found(self, factory, sync_method, kwargs):
        instance = factory(**kwargs)
        with self.assertRaises(NothingFound):
            sync_method(instance.id)

    @parameterized.expand([
        ('movie', ImdbMovieFactory, dict(movie__year=2014, movie__title_en='The Prince')),
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
        cast1 = CastFactory(person=imdb_person.person, movie__title_en='Easy Rider', movie__year=1969,
                            role=self.director)
        cast2 = CastFactory(person=imdb_person.person, movie__title_en='True Romance', movie__year=1994, role=self.actor)
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
