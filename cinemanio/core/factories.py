import random

import factory
from factory.django import DjangoModelFactory
from faker import Faker

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
    title_en = factory.Faker('sentence', nb_words=3, locale='en_US')
    title_ru = factory.Faker('sentence', nb_words=3, locale='ru_RU')
    year = factory.LazyAttribute(lambda o: random.randrange(1900, 2020))

    class Meta:
        model = Movie

    @factory.post_generation
    def genres(self, create, extracted):
        create_m2m_objects(self, create, extracted, 'genres', Genre)

    @factory.post_generation
    def languages(self, create, extracted):
        create_m2m_objects(self, create, extracted, 'languages', Language)

    @factory.post_generation
    def countries(self, create, extracted):
        create_m2m_objects(self, create, extracted, 'countries', Country)


def get_name(prefix, *args):
    return lambda o: getattr(Faker(*args), f'{prefix}_{"male" if o.gender == 1 else "female"}')()


class PersonFactory(DjangoModelFactory):
    gender = factory.LazyAttribute(lambda o: random.choice([Gender.MALE, Gender.FEMALE]))

    first_name = factory.LazyAttribute(get_name('first_name'))
    last_name = factory.LazyAttribute(get_name('last_name'))

    first_name_en = factory.LazyAttribute(get_name('first_name', 'en_US'))
    last_name_en = factory.LazyAttribute(get_name('last_name', 'en_US'))

    first_name_ru = factory.LazyAttribute(get_name('first_name', 'ru_RU'))
    last_name_ru = factory.LazyAttribute(get_name('last_name', 'ru_RU'))

    date_birth = factory.Faker('past_date', start_date="-60y", tzinfo=None)
    date_death = factory.Faker('past_date', start_date="-60y", tzinfo=None)

    class Meta:
        model = Person

    @factory.post_generation
    def roles(self, create, extracted):
        create_m2m_objects(self, create, extracted, 'roles', Role)

    @factory.post_generation
    def country(self, create, extracted):
        if create:
            setattr(self, 'country', extracted if (extracted is not None) else Country.objects.order_by('?').first())


class CastFactory(DjangoModelFactory):
    movie = factory.SubFactory(MovieFactory)
    person = factory.SubFactory(PersonFactory)
    role = factory.LazyAttribute(lambda o: Role.objects.order_by('?').first())

    class Meta:
        model = Cast
