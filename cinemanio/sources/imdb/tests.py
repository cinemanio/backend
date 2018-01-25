from django.test import TestCase

from cinemanio.core.models.factories import MovieFactory, PersonFactory
from cinemanio.sources.imdb.models import ImdbMovie, ImdbPerson


class ImdbTest(TestCase):
    def test_movie_url(self):
        movie = MovieFactory()
        ImdbMovie.objects.create(id=1, movie=movie)
        self.assertEqual(movie.imdb.url, 'http://www.imdb.com/title/tt0000001/')

    def test_person_url(self):
        person = PersonFactory()
        ImdbPerson.objects.create(id=1, person=person)
        self.assertEqual(person.imdb.url, 'http://www.imdb.com/name/nm0000001/')
