import random

from factory.django import DjangoModelFactory
import factory

from cinemanio.core import models


class MovieFactory(DjangoModelFactory):
    year = factory.LazyAttribute(lambda o: random.randrange(1900, 2020))

    class Meta:
        model = models.Movie


class PersonFactory(DjangoModelFactory):
    gender = factory.LazyAttribute(lambda o: random.choice([1, 0]))

    class Meta:
        model = models.Person


class GenreFactory(DjangoModelFactory):
    class Meta:
        model = models.Genre


class RoleFactory(DjangoModelFactory):
    class Meta:
        model = models.Role


class CastFactory(DjangoModelFactory):
    movie = factory.SubFactory(MovieFactory)
    person = factory.SubFactory(PersonFactory)
    role = factory.SubFactory(RoleFactory)

    class Meta:
        model = models.Cast

# class ProfileFactory(DjangoModelFactory):
#     username = factory.LazyAttributeSequence(lambda o, n: 'username%s' % n)
#     email = factory.LazyAttributeSequence(lambda o, n: '%s@example.com' % o.username)
#
#     class Meta:
#         model = models.Profile


# class ListFactory(DjangoModelFactory):
#     author = factory.SubFactory(ProfileFactory)
#
#     class Meta:
#         model = models.List
#
#
# class ListLinkFactory(DjangoModelFactory):
#     user = factory.SubFactory(ProfileFactory)
#
#     class Meta:
#         model = models.ListLink
