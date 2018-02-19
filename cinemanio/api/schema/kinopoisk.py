from graphene_django import DjangoObjectType

from cinemanio.sites.kinopoisk.models import KinopoiskMovie, KinopoiskPerson


class KinopoiskMovieNode(DjangoObjectType):
    class Meta:
        model = KinopoiskMovie


class KinopoiskPersonNode(DjangoObjectType):
    class Meta:
        model = KinopoiskPerson
