import random

from factory.django import DjangoModelFactory
import factory

from cinemanio.core.models import Movie, Person, Genre, Role, Cast


class MovieFactory(DjangoModelFactory):
    year = factory.LazyAttribute(lambda o: random.randrange(1900, 2020))

    class Meta:
        model = Movie


class PersonFactory(DjangoModelFactory):
    gender = factory.LazyAttribute(lambda o: random.choice([1, 0]))

    class Meta:
        model = Person


class GenreFactory(DjangoModelFactory):
    class Meta:
        model = Genre


class RoleFactory(DjangoModelFactory):
    class Meta:
        model = Role


class CastFactory(DjangoModelFactory):
    movie = factory.SubFactory(MovieFactory)
    person = factory.SubFactory(PersonFactory)
    role = factory.SubFactory(RoleFactory)

    class Meta:
        model = Cast
