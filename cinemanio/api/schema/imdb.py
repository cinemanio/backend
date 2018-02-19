from graphene_django import DjangoObjectType

from cinemanio.sites.imdb.models import ImdbMovie, ImdbPerson


class ImdbMovieNode(DjangoObjectType):
    class Meta:
        model = ImdbMovie


class ImdbPersonNode(DjangoObjectType):
    class Meta:
        model = ImdbPerson
