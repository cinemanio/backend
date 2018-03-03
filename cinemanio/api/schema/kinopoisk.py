from graphene import String
from graphene_django import DjangoObjectType

from cinemanio.sites.kinopoisk.models import KinopoiskMovie, KinopoiskPerson


class KinopoiskMovieNode(DjangoObjectType):
    url = String()

    class Meta:
        model = KinopoiskMovie


class KinopoiskPersonNode(DjangoObjectType):
    url = String()

    class Meta:
        model = KinopoiskPerson
