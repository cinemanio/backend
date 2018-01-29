import factory
from factory.django import DjangoModelFactory

from cinemanio.sites.kinopoisk.models import KinopoiskMovie, KinopoiskPerson
from cinemanio.core.factories import MovieFactory, PersonFactory


class KinopoiskMovieFactory(DjangoModelFactory):
    movie = factory.SubFactory(MovieFactory)

    class Meta:
        model = KinopoiskMovie


class KinopoiskPersonFactory(DjangoModelFactory):
    person = factory.SubFactory(PersonFactory)

    class Meta:
        model = KinopoiskPerson
