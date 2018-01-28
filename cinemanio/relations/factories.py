import factory
from factory.django import DjangoModelFactory

from cinemanio.relations.models import MovieRelation, PersonRelation, UserRelation
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
