from parameterized import parameterized

from cinemanio.core.factories import MovieFactory, PersonFactory, CastFactory
from cinemanio.core.tests.base import BaseTestCase, VCRMixin
from cinemanio.sites.wikipedia.models import WikipediaPage
from cinemanio.sites.wikipedia.tasks import sync_movie, sync_person


class WikipediaTest(VCRMixin, BaseTestCase):
    def assert_wikipedia(self, instance, en_title, ru_title, synced=True):
        en = instance.wikipedia.get(lang='en')
        ru = instance.wikipedia.get(lang='ru')
        self.assertEqual(en.title, en_title)
        self.assertEqual(ru.title, ru_title)
        if synced:
            self.assertTrue(en.synced_at)
            self.assertTrue(ru.synced_at)
            self.assertGreater(len(en.content), 2500)
            self.assertGreater(len(ru.content), 2500)

    @parameterized.expand([
        (MovieFactory, 'The Matrix', 'en', 'http://en.wikipedia.org/wiki/The_Matrix'),
        (PersonFactory, 'Dennis Hopper', 'en', 'http://en.wikipedia.org/wiki/Dennis_Hopper'),
    ])
    def test_page_url(self, factory, title, lang, url):
        instance = factory()
        WikipediaPage.objects.create(title=title, lang=lang, content_object=instance)
        self.assertEqual(instance.wikipedia.first().url, url)

    @parameterized.expand([
        (MovieFactory, 'Junk', 'en'),  # disambiguation
        (MovieFactory, 'blablabla', 'en'),  # bad page
    ])
    def test_sync_bad_page(self, factory, title, lang):
        instance = factory()
        page = WikipediaPage.objects.create(content_object=instance, title=title, lang=lang)
        page.sync()
        self.assertIsNone(page.id)
        self.assertEqual(instance.wikipedia.count(), 0)

    @parameterized.expand([
        (MovieFactory, 'The Matrix', 'en', 133093),
        (PersonFactory, 'Dennis Hopper', 'en', 454),
        (MovieFactory, 'Матрица_(фильм)', 'ru', 133093),
        (PersonFactory, 'Хоппер, Деннис', 'ru', 454, 9843),
        (MovieFactory, 'Дворецкий Боб', 'ru'),  # https://github.com/goldsmith/Wikipedia/issues/78
        (MovieFactory, 'Невозвращенец (фильм)', 'ru', 169081)
    ])
    def test_sync_page_with_imdb_id(self, factory, title, lang, imdb_id=None, kinopoisk_id=None):
        instance = factory()
        page = WikipediaPage.objects.create(content_object=instance, title=title, lang=lang)
        page.sync()
        self.assertGreater(len(page.content), 1000)
        if imdb_id:
            self.assertEqual(instance.imdb.id, imdb_id)
            self.assertIsNone(instance.imdb.synced_at)
        if kinopoisk_id:
            self.assertEqual(instance.kinopoisk.id, kinopoisk_id)
            self.assertIsNone(instance.kinopoisk.synced_at)

    @parameterized.expand([
        (MovieFactory, sync_movie,
         dict(year=1999, title_en='The Matrix', title_ru='Матрица'),
         'The Matrix', 'Матрица (фильм)',
         ((dict(person__first_name_en='Keanu', person__last_name_en='Reeves',
                person__first_name_ru='Киану', person__last_name_ru='Ривз'), 'Keanu Reeves', 'Ривз, Киану'),
          (dict(person__first_name_en='Carrie-Anne', person__last_name_en='Moss',
                person__first_name_ru='Керри-Энн', person__last_name_ru='Мосс'), 'Carrie-Anne Moss', 'Мосс, Керри-Энн'),)
         ),
        (PersonFactory, sync_person,
         dict(first_name_en='Dennis', last_name_en='Hopper', first_name_ru='Деннис', last_name_ru='Хоппер'),
         'Dennis Hopper', 'Хоппер, Деннис',
         ((dict(movie__year=1969, movie__title_en='Easy Rider', movie__title_ru='Беспечный ездок'),
           'Easy Rider', 'Беспечный ездок'),
          (dict(movie__year=1956, movie__title_en='Giant', movie__title_ru='Гигант'),
           'Giant (1956 film)', 'Гигант (фильм)'),)
         ),
        # TODO: the right movie is the second search result, not first
        # (MovieFactory, sync_movie,
        #  dict(year=1998, title_en='The Dentist 2', title_ru='Дантист 2'),
        #  'The Dentist 2', 'Дантист 2'),
    ])
    def test_search_and_sync_object_with_roles(self, factory, sync_method, kwargs, en_title, ru_title, roles=()):
        instance = factory(**kwargs)

        # create instances linked to the main
        linked_instances = []
        for role in roles:
            role[0].update({instance._meta.model_name: instance})
            cast = CastFactory(**role[0], role=self.actor)
            field = list(role[0])[0].split('__')[0]
            linked_instances.append(getattr(cast, field))

        sync_method(instance.id)
        self.assert_wikipedia(instance, en_title, ru_title)

        # check instances linked to the main
        for i, role in enumerate(roles):
            self.assert_wikipedia(linked_instances[i], role[1], role[2], synced=False)

    @parameterized.expand([
        (MovieFactory, sync_movie,
         dict(year=1999, title_en='The Matrix', title_ru='Матрица')),
        (PersonFactory, sync_person,
         dict(first_name_en='Dennis', last_name_en='Hopper', first_name_ru='Деннис', last_name_ru='Хоппер')),
    ])
    def test_sync_page_duplicates(self, factory, sync_method, kwargs):
        instance1 = factory(**kwargs)
        instance2 = factory(**kwargs)
        sync_method(instance1.id)
        self.assertGreater(instance1.wikipedia.count(), 0)
        sync_method(instance2.id)
        self.assertEqual(instance2.wikipedia.count(), 0)

    # TODO: write test for WrongValue
    # @parameterized.expand([
    #     ('movie', ImdbMovieFactory, dict(movie__year=2014, movie__title='The Prince')),
    #     ('person', ImdbPersonFactory, dict(person__first_name_en='Allison', person__last_name_en='Williams')),
    # ])
    # def test_sync_page_wrong_value(self, model_name, factory, kwargs):
    #     instance = factory(id=1, **kwargs)
    #     with self.assertRaises(WrongValue):
    #         instance.__class__.objects.create_for(getattr(instance, model_name))

    @parameterized.expand([
        (MovieFactory, sync_movie, dict(year=2005, title_en='', title_ru='')),
        (MovieFactory, sync_movie, dict(year=1984, title_en='Report from the Abyss', title_ru='Репортаж из бездны')),
        (MovieFactory, sync_movie, dict(year=2007, title_en='', title_ru='Нелюбимые')),
        (MovieFactory, sync_movie, dict(year=2006, title_en='', title_ru='Ты - это я')),
        (MovieFactory, sync_movie, dict(year=1998, title_en='I Just Want to Kiss You')),
        (MovieFactory, sync_movie, dict(year=2008, title_en='Senior Skip Day')),
        (MovieFactory, sync_movie, dict(year=1990, title_en='The Killer\'s Edge')),
    ])
    def test_sync_object_with_no_page(self, factory, sync_method, kwargs):
        instance = factory(**kwargs)
        sync_method(instance.id)
        self.assertEqual(instance.wikipedia.count(), 0)
