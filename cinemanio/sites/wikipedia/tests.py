import warnings

from parameterized import parameterized

from cinemanio.core.factories import MovieFactory, PersonFactory, CastFactory
from cinemanio.core.tests.base import BaseTestCase, VCRMixin
from cinemanio.sites.exceptions import WrongValue, PossibleDuplicate
from cinemanio.sites.wikipedia.models import WikipediaPage
from cinemanio.sites.wikipedia.tasks import sync_movie, sync_person

warnings.simplefilter("ignore")


class WikipediaTest(VCRMixin, BaseTestCase):
    def assert_wikipedia(self, instance, en_title, ru_title, synced=True):
        en = instance.wikipedia.get(lang="en")
        ru = instance.wikipedia.get(lang="ru")
        self.assertEqual(en.title, en_title)
        self.assertEqual(ru.title, ru_title)
        if synced:
            self.assertTrue(en.synced_at)
            self.assertTrue(ru.synced_at)
            self.assertGreater(len(en.content), 2500)
            self.assertGreater(len(ru.content), 1000)

    @parameterized.expand(
        [
            (MovieFactory, "The Matrix", "en", "http://en.wikipedia.org/wiki/The_Matrix"),
            (PersonFactory, "Dennis Hopper", "en", "http://en.wikipedia.org/wiki/Dennis_Hopper"),
        ]
    )
    def test_page_url(self, factory, title, lang, url):
        instance = factory()
        WikipediaPage.objects.create(title=title, lang=lang, content_object=instance)
        self.assertEqual(instance.wikipedia.first().url, url)

    @parameterized.expand([(MovieFactory, "xcmvhker", "en")])
    def test_sync_bad_page(self, factory, title, lang):
        instance = factory()
        page = WikipediaPage.objects.create(content_object=instance, title=title, lang=lang)
        page.sync()
        self.assertIsNone(page.id)
        self.assertEqual(instance.wikipedia.count(), 0)

    @parameterized.expand(
        [
            (MovieFactory, "Junk", "Junk (film)", "en", dict(title_en="Junk")),
            (MovieFactory, "Процесс", "Процесс (фильм, 1962)", "ru", dict(year=1962, title_ru="Процесс")),
            # wrong values in e.options
            # (MovieFactory, 'Ариэль (фильм)', 'Ариэль (фильм, 1988)', 'ru', dict(year=1988, title_ru='Ариэль')),
        ]
    )
    def test_sync_disambiguation_page(self, factory, disamb_title, title, lang, kwargs):
        instance = factory(**kwargs)
        page = WikipediaPage.objects.create(content_object=instance, title=disamb_title, lang=lang)
        page.sync()
        self.assertTrue(page.synced_at)
        self.assertEqual(page.title, title)

    @parameterized.expand(
        [
            (MovieFactory, "The Matrix", "en", 133_093),
            (PersonFactory, "Dennis Hopper", "en", 454),
            (MovieFactory, "Матрица_(фильм)", "ru", 133_093),
            (PersonFactory, "Хоппер, Деннис", "ru", 454, 9843),
            (MovieFactory, "Дворецкий Боб", "ru"),  # https://github.com/goldsmith/Wikipedia/issues/78
            (MovieFactory, "Невозвращенец (фильм)", "ru", 169_081),
        ]
    )
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

    @parameterized.expand(
        [
            (
                MovieFactory,
                sync_movie,
                dict(year=1999, title_en="The Matrix", title_ru="Матрица"),
                "The Matrix",
                "Матрица (фильм)",
                (
                    (
                        dict(
                            person__first_name_en="Keanu",
                            person__last_name_en="Reeves",
                            person__first_name_ru="Киану",
                            person__last_name_ru="Ривз",
                        ),
                        "Keanu Reeves",
                        "Ривз, Киану",
                    ),
                    (
                        dict(
                            person__first_name_en="Carrie-Anne",
                            person__last_name_en="Moss",
                            person__first_name_ru="Керри-Энн",
                            person__last_name_ru="Мосс",
                        ),
                        "Carrie-Anne Moss",
                        "Мосс, Керри-Энн",
                    ),
                ),
            ),
            (
                PersonFactory,
                sync_person,
                dict(first_name_en="Dennis", last_name_en="Hopper", first_name_ru="Деннис", last_name_ru="Хоппер"),
                "Dennis Hopper",
                "Хоппер, Деннис",
                (
                    (
                        dict(movie__title_en="Easy Rider", movie__year=1969, movie__title_ru="Беспечный ездок"),
                        "Easy Rider",
                        "Беспечный ездок",
                    ),
                    (
                        dict(movie__title_en="Giant", movie__year=1956, movie__title_ru="Гигант"),
                        "Giant (1956 film)",
                        "Гигант (фильм)",
                    ),
                ),
            ),
            (
                PersonFactory,
                sync_person,
                dict(first_name_en="Brian", last_name_en="Yuzna", first_name_ru="Брайан", last_name_ru="Юзна"),
                "Brian Yuzna",
                "Юзна, Брайан",
                (
                    (
                        dict(movie__title_en="The Dentist", movie__year=1996, movie__title_ru="Дантист"),
                        "The Dentist",
                        "Дантист (фильм)",
                    ),
                    (
                        dict(movie__title_en="The Dentist 2", movie__year=1998, movie__title_ru="Дантист 2"),
                        "The Dentist 2",
                        "Дантист 2",
                    ),
                ),
            ),
            # mess with part numbers, years and (series) pages
            (
                PersonFactory,
                sync_person,
                dict(first_name_en="Wes Craven", last_name_en="Craven", first_name_ru="Уэс", last_name_ru="Крэйвен"),
                "Wes Craven",
                "Крэйвен, Уэс",
                (
                    (
                        dict(movie__title_en="Scream", movie__year=1996, movie__title_ru="Крик"),
                        "Scream (1996 film)",
                        "Крик (фильм, 1996)",
                    ),
                    (dict(movie__title_en="Scream 2", movie__year=1997, movie__title_ru="Крик 2"), "Scream 2", "Крик 2"),
                    (dict(movie__title_en="Scream 3", movie__year=2000, movie__title_ru="Крик 3"), "Scream 3", "Крик 3"),
                ),
            ),
            # when term with year the right movie is the second search results, not first
            (
                MovieFactory,
                sync_movie,
                dict(year=1998, title_en="The Dentist 2", title_ru="Дантист 2"),
                "The Dentist 2",
                "Дантист 2",
            ),
        ]
    )
    def test_search_and_sync_object_with_roles(self, factory, sync_method, kwargs, en_title, ru_title, roles=()):
        instance = factory(**kwargs)

        # create instances linked to the main
        linked_instances = []
        for role in roles:
            role[0].update({instance._meta.model_name: instance})
            cast = CastFactory(**role[0], role=self.actor)
            field = list(role[0])[0].split("__")[0]
            linked_instances.append(getattr(cast, field))

        sync_method(instance.id)
        self.assert_wikipedia(instance, en_title, ru_title)

        # check instances linked to the main
        for i, role in enumerate(roles):
            self.assert_wikipedia(linked_instances[i], role[1], role[2], synced=False)

    @parameterized.expand(
        [
            (MovieFactory, "en", dict(year=1999, title_en="The Matrix", title_ru="Матрица")),
            (
                PersonFactory,
                "en",
                dict(first_name_en="Dennis", last_name_en="Hopper", first_name_ru="Деннис", last_name_ru="Хоппер"),
            ),
        ]
    )
    def test_sync_page_duplicates(self, factory, lang, kwargs):
        instance1 = factory(**kwargs)
        instance2 = factory(**kwargs)
        WikipediaPage.objects.create_for(instance1, lang)
        self.assertEqual(instance1.wikipedia.count(), 1)
        with self.assertRaises(PossibleDuplicate):
            WikipediaPage.objects.create_for(instance2, lang)

    @parameterized.expand(
        [
            (MovieFactory, "en", dict(year=1999, title_en="The Matrix", title_ru="Матрица")),
            (
                PersonFactory,
                "en",
                dict(first_name_en="Dennis", last_name_en="Hopper", first_name_ru="Деннис", last_name_ru="Хоппер"),
            ),
        ]
    )
    def test_sync_page_wrong_value(self, factory, lang, kwargs):
        instance = factory(**kwargs)
        WikipediaPage.objects.create(lang=lang, title="anything", content_object=instance)
        with self.assertRaises(WrongValue):
            WikipediaPage.objects.create_for(instance, lang)

    @parameterized.expand(
        [
            (MovieFactory, sync_movie, dict(year=2005, title_en="", title_ru="")),
            (MovieFactory, sync_movie, dict(year=1984, title_en="Report from the Abyss", title_ru="Репортаж из бездны")),
            (MovieFactory, sync_movie, dict(year=2007, title_en="", title_ru="Нелюбимые")),
            (MovieFactory, sync_movie, dict(year=2006, title_en="", title_ru="Ты - это я")),
            (MovieFactory, sync_movie, dict(year=1998, title_en="I Just Want to Kiss You")),
            (MovieFactory, sync_movie, dict(year=2008, title_en="Senior Skip Day")),
            (MovieFactory, sync_movie, dict(year=1990, title_en="The Killer's Edge")),
        ]
    )
    def test_sync_object_with_no_page(self, factory, sync_method, kwargs):
        instance = factory(**kwargs)
        sync_method(instance.id)
        self.assertEqual(instance.wikipedia.count(), 0)
