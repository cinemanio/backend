from datetime import timedelta
from django.utils import timezone
from django.urls.base import reverse
from django.contrib.contenttypes.models import ContentType
from vcr_unittest import VCRMixin
from parameterized import parameterized

from cinemanio.core.factories import MovieFactory, PersonFactory
from cinemanio.core.tests.base import BaseTestCase
from cinemanio.core.tests.admin import AdminBaseTest
from cinemanio.sites.imdb.factories import ImdbMovieFactory, ImdbPersonFactory
from cinemanio.sites.imdb.tests.mixins import ImdbSyncMixin
from cinemanio.sites.kinopoisk.factories import KinopoiskPersonFactory, KinopoiskMovieFactory
from cinemanio.sites.kinopoisk.tests.mixins import KinopoiskSyncMixin
from cinemanio.sites.wikipedia.factories import WikipediaPageFactory

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
        self.assertEqual(Movie.objects.filter(kinopoisk=None).count(), 3)
        self.assertEqual(Movie.objects.filter(imdb=None).count(), 16)
        self.assertListEqual(list(Movie.objects.filter(kinopoisk=None).values_list('title_en', flat=True)),
                             ['Made for Each Other',
                              "Bad Boy's 10th Anniversary... The Hits",
                              'Screen Test: Dennis Hopper'])
        self.assertListEqual(list(Movie.objects.filter(imdb=None).values_list('title_en', flat=True)),
                             ['In the Lines of My Hand',
                              'No Subtitles Necessary: Laszlo & Vilmos',
                              'The Brothers Warner',
                              '3055 Jean Leon',
                              'Essential Gorillaz',
                              'Gorillaz: Live in Manchester',
                              'The Source: The Story of the Beats and the Beat Generation',
                              'Motion and Emotion: The Films of Wim Wenders',
                              'Hollywood, No Sex Please!',
                              'Electric Boogaloo: The Wild, Untold Story of Cannon Films',
                              "Corman's World: Exploits of a Hollywood Rebel",
                              'Me and Will',
                              'Forever James Dean',
                              'Apocalypse Pooh',
                              'Henry Fonda: The Man and His Movies',
                              'Apocalypse Now: The Workprint'])

        self.assertEqual(Movie.objects.filter(title='').count(), 0)
        self.assertEqual(Movie.objects.filter(title_en='').count(), 0)
        self.assertEqual(Movie.objects.filter(title_ru='').count(), 28)
        self.assertEqual(Movie.objects.filter(year=None).count(), 0)

        movie = Movie.objects.get(imdb__id=172794)
        self.assertEqual(movie.title_ru, 'Почерк убийцы')  # ru title from kinopoisk
        self.assertEqual(movie.title_en, 'The Apostate')  # en title from imdb
        self.assertEqual(movie.title_original, 'Michael Angel')  # original title from kinopoisk
        self.assertEqual(movie.year, 2000)  # 1999 on kinopoisk

    def test_sync_all_roles_of_movie_from_imdb_and_kinopoisk(self):
        imdb_movie = ImdbMovieFactory(id=64276)  # easy rider
        movie = imdb_movie.movie
        kp_movie = KinopoiskMovieFactory(id=4220, movie=movie)

        kp_movie.sync(roles='all')
        self.assertEqual(movie.cast.count(), 60)
        self.assertEqual(Person.objects.count(), 56)

        imdb_movie.sync(roles='all')
        self.assertEqual(movie.cast.count(), 60)
        self.assertEqual(Person.objects.count(), 56)

        self.assertEqual(Person.objects.filter(kinopoisk=None).count(), 0)
        self.assertEqual(Person.objects.filter(imdb=None).count(), 0)
        self.assertEqual(Person.objects.filter(first_name='').count(), 0)
        self.assertEqual(Person.objects.filter(last_name='').count(), 0)
        self.assertEqual(Person.objects.filter(first_name_en='').count(), 0)
        self.assertEqual(Person.objects.filter(last_name_en='').count(), 0)
        self.assertEqual(Person.objects.filter(first_name_ru='').count(), 0)
        self.assertEqual(Person.objects.filter(last_name_ru='').count(), 0)

    def test_sync_all_roles_of_ru_movie_from_imdb_and_kinopoisk(self):
        imdb_movie = ImdbMovieFactory(id=69293)  # solaris
        movie = imdb_movie.movie
        kp_movie = KinopoiskMovieFactory(id=43911, movie=movie)

        kp_movie.sync(roles='all')
        self.assertEqual(movie.cast.count(), 28)
        self.assertEqual(Person.objects.count(), 27)

        imdb_movie.sync(roles='all')
        self.assertEqual(movie.cast.count(), 39)
        self.assertEqual(Person.objects.count(), 37)

        self.assertEqual(Person.objects.exclude(kinopoisk=None).exclude(imdb=None).count(), 18)  # found by translit
        self.assertEqual(Person.objects.filter(kinopoisk=None).count(), 10)
        self.assertEqual(Person.objects.filter(imdb=None).count(), 9)
        self.assertListEqual([p.name for p in Person.objects.filter(kinopoisk=None)],
                             ['Andrei Tarkovsky',
                              'Jüri Järvet',
                              'Sos Sargsyan',
                              'Yulian Semyonov',
                              'Raimundas Banionis',
                              'Artyom Karapetyan',
                              'Vladimir Tatosov',
                              'Vladimir Zamanskiy',
                              'Nina Marcus',
                              'Stanislaw Lem'])
        self.assertListEqual([p.name for p in Person.objects.filter(imdb=None)],
                             ['Andrey Tarkovskiy',
                              'Yuri Yarvet',
                              'Sos Sarkisyan',
                              'Yulian Semenov',
                              'Raymundas Banionis',
                              'Vyacheslav Tarasov',
                              'Stanislav Lem',
                              'Eduard Artemev',
                              'Nina Markus'])

        self.assertEqual(Person.objects.filter(first_name='').count(), 0)
        self.assertEqual(Person.objects.filter(last_name='').count(), 0)
        self.assertEqual(Person.objects.filter(first_name_en='').count(), 0)
        self.assertEqual(Person.objects.filter(last_name_en='').count(), 0)
        self.assertEqual(Person.objects.filter(first_name_ru='').count(), 0)
        self.assertEqual(Person.objects.filter(last_name_ru='').count(), 0)

        # check translated role names
        role = movie.cast.get(person__kinopoisk__id=185619)
        self.assertEqual(role.name_ru, 'Хари')
        self.assertEqual(role.name_en, 'Khari')


class PopulateMixin:
    def populate(self, factory, site_factory, args=None):
        def get_kwargs():
            kwargs = {}
            if site_factory == WikipediaPageFactory:
                kwargs = dict(lang=args[1], content_object=factory())
            return kwargs

        for i in range(10):
            factory()
        for i in range(10):
            site_factory(synced_at=timezone.now(), **get_kwargs())
        for i in range(5):
            site_factory(synced_at=timezone.now() - timedelta(days=9999), **get_kwargs())


class SitesManagersTest(BaseTestCase, PopulateMixin):
    @parameterized.expand([
        (Movie, MovieFactory, ImdbMovieFactory, ('imdb',)),
        (Person, PersonFactory, ImdbPersonFactory, ('imdb',)),
        (Movie, MovieFactory, KinopoiskMovieFactory, ('kinopoisk',)),
        (Person, PersonFactory, KinopoiskPersonFactory, ('kinopoisk',)),
        (Movie, MovieFactory, WikipediaPageFactory, ('wikipedia', 'en')),
        (Person, PersonFactory, WikipediaPageFactory, ('wikipedia', 'en')),
    ])
    def test_sites_manager_methods(self, model, factory, site_factory, args):
        self.populate(factory, site_factory, args)
        self.assertEqual(model.sites.without_site(*args).count(), 10)
        self.assertEqual(model.sites.with_site(*args).count(), 15)
        self.assertEqual(model.sites.with_site_uptodate(*args).count(), 10)
        self.assertEqual(model.sites.with_site_outdated(*args).count(), 5)


class SitesAdminTest(AdminBaseTest, PopulateMixin):
    def setUp(self):
        super().setUp()
        self._login('admin')

    @parameterized.expand([
        (Movie, MovieFactory, ImdbMovieFactory, 'imdb'),
        (Person, PersonFactory, ImdbPersonFactory, 'imdb'),
        (Movie, MovieFactory, KinopoiskMovieFactory, 'kinopoisk'),
        (Person, PersonFactory, KinopoiskPersonFactory, 'kinopoisk'),
        (Movie, MovieFactory, WikipediaPageFactory, 'wikipedia_en'),
        (Person, PersonFactory, WikipediaPageFactory, 'wikipedia_en'),
    ])
    def test_objects_page_sites_filtration(self, model, factory, site_factory, param):
        # this request to cache ContentType value
        ContentType.objects.get_for_model(model)
        self.populate(factory, site_factory, param.split('_'))
        object_type = model._meta.model_name
        for value in ['present', 'no', 'uptodate', 'outdated']:
            with self.assertNumQueries(9):
                response = self.client.get(reverse(f'admin:core_{object_type}_changelist') + f'?{param}={value}')
            self.assertEqual(response.status_code, 200)
