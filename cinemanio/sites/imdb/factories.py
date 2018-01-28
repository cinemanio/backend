import factory
from factory.django import DjangoModelFactory

from cinemanio.sites.imdb.models import ImdbMovie, ImdbPerson
from cinemanio.core.factories import MovieFactory, PersonFactory


class ImdbMovieFactory(DjangoModelFactory):
    movie = factory.SubFactory(MovieFactory)

    class Meta:
        model = ImdbMovie


class ImdbPersonFactory(DjangoModelFactory):
    person = factory.SubFactory(PersonFactory)

    class Meta:
        model = ImdbPerson
