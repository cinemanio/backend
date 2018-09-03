import factory
import random
from factory.django import DjangoModelFactory

from cinemanio.relations.models import (MovieRelation, PersonRelation, UserRelation,
                                        MovieRelationCount, PersonRelationCount)
from cinemanio.core.factories import MovieFactory, PersonFactory
from cinemanio.users.factories import UserFactory


class MovieRelationFactory(DjangoModelFactory):
    object = factory.SubFactory(MovieFactory)
    user = factory.SubFactory(UserFactory)

    class Meta:
        model = MovieRelation


class PersonRelationFactory(DjangoModelFactory):
    object = factory.SubFactory(PersonFactory)
    user = factory.SubFactory(UserFactory)

    class Meta:
        model = PersonRelation


class UserRelationFactory(DjangoModelFactory):
    object = factory.SubFactory(UserFactory)
    user = factory.SubFactory(UserFactory)

    class Meta:
        model = UserRelation


class MovieRelationCountFactory(DjangoModelFactory):
    object = factory.SubFactory(MovieFactory)
    fav = factory.LazyAttribute(lambda o: random.randrange(0, 1000))

    class Meta:
        model = MovieRelationCount


class PersonRelationCountFactory(DjangoModelFactory):
    object = factory.SubFactory(PersonFactory)
    fav = factory.LazyAttribute(lambda o: random.randrange(0, 1000))

    class Meta:
        model = PersonRelationCount
