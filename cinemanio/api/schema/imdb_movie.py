from graphene_django import DjangoObjectType

from cinemanio.sites.imdb.models import ImdbMovie


class ImdbMovieNode(DjangoObjectType):
    class Meta:
        model = ImdbMovie
