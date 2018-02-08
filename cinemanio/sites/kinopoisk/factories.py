import factory
from factory.django import DjangoModelFactory

from cinemanio.sites.kinopoisk.models import KinopoiskMovie, KinopoiskPerson
from cinemanio.core.factories import MovieFactory, PersonFactory


class KinopoiskMovieFactory(DjangoModelFactory):
    id = factory.Sequence(lambda n: n)
    movie = factory.SubFactory(MovieFactory)

    class Meta:
        model = KinopoiskMovie


class KinopoiskPersonFactory(DjangoModelFactory):
    id = factory.Sequence(lambda n: n)
    person = factory.SubFactory(PersonFactory)

    class Meta:
        model = KinopoiskPerson
