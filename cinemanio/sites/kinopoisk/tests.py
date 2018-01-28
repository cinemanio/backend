from django.test import TestCase

from cinemanio.core.factories import MovieFactory, PersonFactory
from cinemanio.sites.kinopoisk.models import KinopoiskMovie, KinopoiskPerson


class KinopoiskTest(TestCase):
    def test_movie_url(self):
        movie = MovieFactory()
        KinopoiskMovie.objects.create(id=1, movie=movie)
        self.assertEqual(movie.kinopoisk.url, 'http://www.kinopoisk.ru/film/1/')

    def test_person_url(self):
        person = PersonFactory()
        KinopoiskPerson.objects.create(id=1, person=person)
        self.assertEqual(person.kinopoisk.url, 'http://www.kinopoisk.ru/name/1/')
