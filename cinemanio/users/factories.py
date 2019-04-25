from factory.django import DjangoModelFactory
import factory

from cinemanio.users.models import User


class UserFactory(DjangoModelFactory):
    username = factory.LazyAttributeSequence(lambda o, n: 'username%s' % n)
    email = factory.Faker('email')
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')

    class Meta:
        model = User
