from graphene import String
from graphene_django import DjangoObjectType

from cinemanio.sites.imdb.models import ImdbMovie, ImdbPerson


class ImdbMovieNode(DjangoObjectType):
    url = String()

    class Meta:
        model = ImdbMovie


class ImdbPersonNode(DjangoObjectType):
    url = String()

    class Meta:
        model = ImdbPerson
