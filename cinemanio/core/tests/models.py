from unittest import skip
from django.core.exceptions import ValidationError
from django.utils import translation

from cinemanio.core.factories import MovieFactory, PersonFactory, CastFactory
from cinemanio.core.models import Movie, Person, Cast, Role, Gender
from cinemanio.core.tests.base import BaseTestCase


class ModelsTest(BaseTestCase):
    def easy_rider(self):
        return MovieFactory(title_en='Easy Rider', title_ru='Беспечный Ездок', year=1969)

    def jack(self):
        return PersonFactory(first_name_en='Jack', last_name_en='Nicholson',
                             first_name_ru='Джек', last_name_ru='Николсон')

    @skip('Now validation occurs not on model, but on form level')
    def test_movie_year(self):
        with self.assertRaises(ValidationError):
            MovieFactory(year=0)
        with self.assertRaises(ValidationError):
            MovieFactory(year=2100)

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

    def test_person_roles(self):
        person = PersonFactory(roles=[])
        CastFactory(person=person, role=Role.objects.get_scenarist())
        for i in range(9):
            CastFactory(person=person, role=Role.objects.get_actor())
        person.set_roles()
        self.assertQuerysetEqual(person.roles.all(), [Role.objects.get_actor().name])

        # exceed threshold
        CastFactory(person=person, role=Role.objects.get_scenarist())
        person.set_roles()
        self.assertQuerysetEqual(person.roles.all(), [Role.objects.get_actor().name, Role.objects.get_scenarist().name])

    def test_movie_title_transliteration(self):
        movie = MovieFactory(title='', title_en='', title_ru='Ирония судьбы, или с легким паром!')
        self.assertEqual(len(movie.title), 0)
        movie.set_transliteratable_fields()
        self.assertEqual(movie.title, movie.title_en)
        self.assertGreater(len(movie.title), 0)

    def test_person_name_transliteration(self):
        person = PersonFactory(first_name='', last_name='', first_name_en='', last_name_en='',
                               first_name_ru='Андрей', last_name_ru='Мягков')
        self.assertEqual(len(person.name), 0)
        person.set_transliteratable_fields()
        self.assertEqual(person.name, person.name_en)
        self.assertGreater(len(person.name), 0)

    def test_person_gender(self):
        for i in range(100):
            PersonFactory()
        self.assertEqual(Person.objects.filter(gender=None).count(), 0)
        self.assertGreater(Person.objects.filter(gender=Gender.MALE).count(), 0)
        self.assertGreater(Person.objects.filter(gender=Gender.FEMALE).count(), 0)
