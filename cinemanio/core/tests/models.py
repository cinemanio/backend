from django.utils import translation

from cinemanio.core.models import Movie, Person, Cast, Role
from cinemanio.core.models.factories import MovieFactory, PersonFactory, CastFactory
from cinemanio.core.tests.base import BaseTestCase


class ModelsTest(BaseTestCase):
    def easy_rider(self):
        return MovieFactory(title_en='Easy Rider', title_ru='Беспечный Ездок', year=1969)

    def jack(self):
        return PersonFactory(first_name_en='Jack', last_name_en='Nicholson',
                             first_name_ru='Джек', last_name_ru='Николсон')

    def test_movie_with_cast(self):
        movie = MovieFactory()
        movie.cast.add(CastFactory())
        movie.cast.add(CastFactory())

        self.assertEqual(Person.objects.count(), 2)
        self.assertEqual(Cast.objects.count(), 2)
        self.assertEqual(movie.cast.count(), 2)

    def test_person_with_career(self):
        person = PersonFactory()
        person.career.add(CastFactory())
        person.career.add(CastFactory())

        self.assertEqual(Movie.objects.count(), 2)
        self.assertEqual(Cast.objects.count(), 2)
        self.assertEqual(person.career.count(), 2)

    def test_movie_repr(self):
        movie = self.easy_rider()
        translation.activate('en')
        self.assertEqual(repr(movie), 'Easy Rider (1969)')
        translation.activate('ru')
        self.assertEqual(repr(movie), 'Беспечный Ездок (Easy Rider, 1969)')

    def test_person_repr(self):
        person = self.jack()
        translation.activate('en')
        self.assertEqual(repr(person), 'Jack Nicholson')
        translation.activate('ru')
        self.assertEqual(repr(person), 'Джек Николсон, Jack Nicholson')

    def test_cast_repr(self):
        cast = CastFactory(movie=self.easy_rider(), person=self.jack(),
                           role=Role.objects.get_actor(), name_en='George Hanson', name_ru='Джордж Хэнсон')
        translation.activate('en')
        self.assertEqual(repr(cast), 'Easy Rider - Jack Nicholson (actor: George Hanson)')
        translation.activate('ru')
        self.assertEqual(repr(cast), 'Беспечный Ездок - Джек Николсон (актер: Джордж Хэнсон)')
