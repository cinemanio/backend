from django.test import TestCase

from cinemanio.core.models.person import ACTOR_ID
from cinemanio.core.models import Movie, Person, Cast, Role
from cinemanio.core.models.factories import MovieFactory, PersonFactory, CastFactory


class ModelsTest(TestCase):
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
        movie = MovieFactory(title='Ну погоди!', year=2010)
        self.assertEqual(repr(movie), 'Ну погоди! (2010)')

    def test_person_repr(self):
        person = PersonFactory(first_name='Jimi', last_name='Hendrix')
        self.assertEqual(repr(person), 'Jimi Hendrix')

    def test_cast_repr(self):
        Role.objects.create(id=ACTOR_ID, name='actor')  # TODO: move to fixtures
        movie = MovieFactory(title='Ну погоди!', year=2010)
        person = PersonFactory(first_name='Jimi', last_name='Hendrix')
        cast = CastFactory(movie=movie, person=person, role=Role.objects.get_actor(), name='wolf')
        self.assertEqual(repr(cast), 'Ну погоди! - Jimi Hendrix (actor: wolf)')
