from django.test import TestCase

from cinemanio.core.models.factories import MovieFactory, PersonFactory
from cinemanio.sources.wikipedia.models import WikipediaPage


class WikipediaTest(TestCase):
    def test_movie_url(self):
        movie = MovieFactory()
        WikipediaPage.objects.create(name='Matrix', lang='en', content_object=movie)
        self.assertEqual(movie.wikipedia.first().url, 'http://en.wikipedia.org/wiki/Matrix')
