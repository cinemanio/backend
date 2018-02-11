from django.test import TestCase

from cinemanio.core.factories import MovieFactory, PersonFactory
from cinemanio.sites.wikipedia.models import WikipediaPage


class WikipediaTest(TestCase):
    def test_movie_url(self):
        movie = MovieFactory()
        WikipediaPage.objects.create(name='Matrix', lang='en', content_object=movie)
        self.assertEqual(movie.wikipedia.first().url, 'http://en.wikipedia.org/wiki/Matrix')

    def test_person_url(self):
        person = PersonFactory()
        WikipediaPage.objects.create(name='Matrix', lang='en', content_object=person)
        self.assertEqual(person.wikipedia.first().url, 'http://en.wikipedia.org/wiki/Matrix')
