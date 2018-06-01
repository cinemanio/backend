import random

import factory
from factory.django import DjangoModelFactory

from cinemanio.core.models import Movie, Person, Genre, Language, Country, Role, Cast, Gender


class GenreFactory(DjangoModelFactory):
    class Meta:
        model = Genre


class LanguageFactory(DjangoModelFactory):
    class Meta:
        model = Language


class CountryFactory(DjangoModelFactory):
    class Meta:
        model = Country


def create_m2m_objects(self, create, extracted, relation_name, model):
    if create:
        value = extracted if (extracted is not None) else model.objects.order_by('?')[:random.randint(1, 4)]
        getattr(self, relation_name).set(value)


class MovieFactory(DjangoModelFactory):
    title = factory.Faker('sentence', nb_words=3)
    year = factory.LazyAttribute(lambda o: random.randrange(1900, 2020))

    class Meta:
        model = Movie

    @factory.post_generation
    def genres(self, create, extracted, **kwargs):
        create_m2m_objects(self, create, extracted, 'genres', Genre)

    @factory.post_generation
    def languages(self, create, extracted, **kwargs):
        create_m2m_objects(self, create, extracted, 'languages', Language)

    @factory.post_generation
    def countries(self, create, extracted, **kwargs):
        create_m2m_objects(self, create, extracted, 'countries', Country)


class PersonFactory(DjangoModelFactory):
    gender = factory.LazyAttribute(lambda o: random.choice([Gender.MALE, Gender.FEMALE]))
    country = factory.SubFactory(CountryFactory)

    first_name = factory.Faker('sentence', nb_words=1)
    last_name = factory.Faker('sentence', nb_words=1)

    first_name_en = factory.Faker('sentence', nb_words=1)
    last_name_en = factory.Faker('sentence', nb_words=1)

    first_name_ru = factory.Faker('sentence', nb_words=1)
    last_name_ru = factory.Faker('sentence', nb_words=1)

    date_birth = factory.Faker('past_date', start_date="-60y", tzinfo=None)
    date_death = factory.Faker('past_date', start_date="-60y", tzinfo=None)

    class Meta:
        model = Person

    @factory.post_generation
    def roles(self, create, extracted, **kwargs):
        create_m2m_objects(self, create, extracted, 'roles', Role)


class CastFactory(DjangoModelFactory):
    movie = factory.SubFactory(MovieFactory)
    person = factory.SubFactory(PersonFactory)
    role = factory.LazyAttribute(lambda o: Role.objects.order_by('?')[0])

    class Meta:
        model = Cast
