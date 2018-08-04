from django.test import TestCase
from parameterized import parameterized
from vcr_unittest import VCRMixin

from cinemanio.core.tests.base import VCRAddNewMixin
from cinemanio.core.factories import MovieFactory, PersonFactory
from cinemanio.sites.exceptions import PossibleDuplicate
from cinemanio.sites.wikipedia.models import WikipediaPage
from cinemanio.sites.wikipedia.tasks import sync_movie, sync_person


class WikipediaTest(VCRMixin, VCRAddNewMixin, TestCase):
    @parameterized.expand([
        (MovieFactory, 'The Matrix', 'en', 'http://en.wikipedia.org/wiki/The_Matrix'),
        (PersonFactory, 'Dennis Hopper', 'en', 'http://en.wikipedia.org/wiki/Dennis_Hopper'),
    ])
    def test_page_url(self, factory, name, lang, url):
        instance = factory()
        WikipediaPage.objects.create(name=name, lang=lang, content_object=instance)
        self.assertEqual(instance.wikipedia.first().url, url)

    @parameterized.expand([
        (MovieFactory, 'Junk', 'en'),  # disambiguation
        (MovieFactory, 'blablabla', 'en'),  # bad page
    ])
    def test_sync_bad_page(self, factory, name, lang):
        instance = factory()
        page = WikipediaPage.objects.create(content_object=instance, name=name, lang=lang)
        page.sync()
        self.assertIsNone(page.id)
        self.assertEqual(instance.wikipedia.count(), 0)

    @parameterized.expand([
        (MovieFactory, 'The Matrix', 'en', 133093),
        (PersonFactory, 'Dennis Hopper', 'en', 454),
        (MovieFactory, 'Матрица_(фильм)', 'ru', 133093),
        (PersonFactory, 'Хоппер, Деннис', 'ru', 454, 9843),
        (MovieFactory, 'Дворецкий Боб', 'ru'),  # https://github.com/goldsmith/Wikipedia/issues/78
    ])
    def test_sync_page_with_imdb_id(self, factory, name, lang, imdb_id=None, kinopoisk_id=None):
        instance = factory()
        page = WikipediaPage.objects.create(content_object=instance, name=name, lang=lang)
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
         'The Matrix', 'Матрица (фильм)'),
        (PersonFactory, sync_person,
         dict(first_name_en='Dennis', last_name_en='Hopper', first_name_ru='Деннис', last_name_ru='Хоппер'),
         'Dennis Hopper', 'Хоппер, Деннис'),
    ])
    def test_search_and_sync_page(self, factory, sync_method, kwargs, en_name, ru_name):
        instance = factory(**kwargs)
        sync_method(instance.id)
        en = instance.wikipedia.get(lang='en')
        ru = instance.wikipedia.get(lang='ru')
        self.assertEqual(en.name, en_name)
        self.assertEqual(ru.name, ru_name)
        self.assertTrue(en.synced_at)
        self.assertTrue(ru.synced_at)
        self.assertGreater(len(en.content), 2500)
        self.assertGreater(len(ru.content), 2500)

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
        with self.assertRaises(PossibleDuplicate):
            sync_method(instance2.id)
