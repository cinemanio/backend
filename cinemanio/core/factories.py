import random

import factory
from factory.django import DjangoModelFactory

from cinemanio.core.models import Movie, Person, Genre, Language, Country, Role, Cast


class MovieFactory(DjangoModelFactory):
    title = factory.Faker('sentence', nb_words=3)
    year = factory.LazyAttribute(lambda o: random.randrange(1900, 2020))

    class Meta:
        model = Movie

    @factory.post_generation
    def genres(self, create, extracted, **kwargs):
        if create:
            self.genres.set(extracted or Genre.objects.order_by('?')[:random.randint(1, 4)])

    @factory.post_generation
    def languages(self, create, extracted, **kwargs):
        if create:
            self.languages.set(extracted or Language.objects.order_by('?')[:random.randint(1, 4)])

    @factory.post_generation
    def countries(self, create, extracted, **kwargs):
        if create:
            self.countries.set(extracted or Country.objects.order_by('?')[:random.randint(1, 4)])


class PersonFactory(DjangoModelFactory):
    gender = factory.LazyAttribute(lambda o: random.choice([1, 0]))
    first_name_en = ''
    last_name_en = ''

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
