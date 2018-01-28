import factory
from factory.django import DjangoModelFactory

from cinemanio.attitudes.models import MovieAttitude, PersonAttitude, UserAttitude
from cinemanio.core.factories import MovieFactory, PersonFactory
from cinemanio.users.factories import UserFactory


class MovieAttitudeFactory(DjangoModelFactory):
    object = factory.SubFactory(MovieFactory)
    user = factory.SubFactory(UserFactory)

    class Meta:
        model = MovieAttitude


class PersonAttitudeFactory(DjangoModelFactory):
    object = factory.SubFactory(PersonFactory)
    user = factory.SubFactory(UserFactory)

    class Meta:
        model = PersonAttitude


class UserAttitudeFactory(DjangoModelFactory):
    object = factory.SubFactory(UserFactory)
    user = factory.SubFactory(UserFactory)

    class Meta:
        model = UserAttitude
