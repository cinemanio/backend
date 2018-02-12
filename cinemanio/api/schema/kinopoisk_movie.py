from graphene_django import DjangoObjectType

from cinemanio.sites.kinopoisk.models import KinopoiskMovie


class KinopoiskMovieNode(DjangoObjectType):
    class Meta:
        model = KinopoiskMovie
