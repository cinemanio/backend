import graphene
from graphene import relay
from graphene_django.filter import DjangoFilterConnectionField

from cinemanio.api.schema.movie import MovieNode
from cinemanio.api.schema.person import PersonNode


class Query:
    movie = relay.Node.Field(MovieNode)
    person = relay.Node.Field(PersonNode)

    movies = DjangoFilterConnectionField(MovieNode)
    persons = DjangoFilterConnectionField(PersonNode)
