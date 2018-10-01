from factory.django import DjangoModelFactory
import factory

from cinemanio.users.models import User


class UserFactory(DjangoModelFactory):
    username = factory.LazyAttributeSequence(lambda o, n: "username%s" % n)
    email = factory.LazyAttributeSequence(lambda o, n: "%s@example.com" % o.username)

    class Meta:
        model = User
