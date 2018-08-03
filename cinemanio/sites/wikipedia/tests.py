from django.test import TestCase
from vcr_unittest import VCRMixin

from cinemanio.core.factories import MovieFactory, PersonFactory
from cinemanio.sites.wikipedia.models import WikipediaPage
from cinemanio.sites.wikipedia.tasks import sync_movie, sync_person
from cinemanio.sites.exceptions import PossibleDuplicate


class WikipediaTest(VCRMixin, TestCase):
    def movie_matrix(self):
        return MovieFactory(year=1999, title_en='The Matrix', title_ru='Матрица')

    def person_dennis_hopper(self):
        return PersonFactory(first_name_en='Dennis', last_name_en='Hopper',
                             first_name_ru='Деннис', last_name_ru='Хоппер')

    def test_movie_url(self):
        movie = MovieFactory()
        WikipediaPage.objects.create(name='Matrix', lang='en', content_object=movie)
        self.assertEqual(movie.wikipedia.first().url, 'http://en.wikipedia.org/wiki/Matrix')

    def test_person_url(self):
        person = PersonFactory()
        WikipediaPage.objects.create(name='Matrix', lang='en', content_object=person)
        self.assertEqual(person.wikipedia.first().url, 'http://en.wikipedia.org/wiki/Matrix')

    def test_sync_movie_page(self):
        movie = MovieFactory()
        page = WikipediaPage.objects.create(content_object=movie, name='Easy_Rider', lang='en')
        page.sync()
        self.assertGreater(len(page.content), 20000)

    def test_search_and_sync_movie_matrix(self):
        movie = self.movie_matrix()
        sync_movie(movie.id)
        en = movie.wikipedia.get(lang='en')
        ru = movie.wikipedia.get(lang='ru')
        self.assertEqual(en.name, 'The Matrix')
        self.assertEqual(ru.name, 'Матрица (фильм)')
        self.assertGreater(len(en.content), 50000)
        self.assertGreater(len(ru.content), 2500)

    def test_search_and_sync_person_dennis_hopper(self):
        person = self.person_dennis_hopper()
        sync_person(person.id)
        en = person.wikipedia.get(lang='en')
        ru = person.wikipedia.get(lang='ru')
        self.assertEqual(en.name, 'Dennis Hopper')
        self.assertEqual(ru.name, 'Хоппер, Деннис')
        self.assertGreater(len(en.content), 25000)
        self.assertGreater(len(ru.content), 10000)

    def test_sync_movie_duplicates(self):
        movie1 = self.movie_matrix()
        movie2 = self.movie_matrix()
        sync_movie(movie1.id)
        self.assertGreater(movie1.wikipedia.count(), 0)
        with self.assertRaises(PossibleDuplicate):
            sync_movie(movie2.id)

    def test_sync_person_duplicates(self):
        person1 = self.person_dennis_hopper()
        person2 = self.person_dennis_hopper()
        sync_person(person1.id)
        self.assertGreater(person1.wikipedia.count(), 0)
        with self.assertRaises(PossibleDuplicate):
            sync_person(person2.id)
