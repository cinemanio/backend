import graphene
from graphene import relay
from graphene_django import DjangoObjectType

from cinemanio.api.utils import DjangoObjectTypeMixin, DjangoFilterConnectionField
from cinemanio.api.schema.cast import CastNode
from cinemanio.core.models import Movie


class MovieNode(DjangoObjectTypeMixin, DjangoObjectType):
    cast = DjangoFilterConnectionField(CastNode)

    class Meta:
        model = Movie
        filter_fields = ['year', 'genres', 'countries', 'languages']
        interfaces = (relay.Node,)

    def resolve_cast(self, info, *args, **kwargs):
        return CastNode.get_queryset(info)


class MovieQuery:
    movie = graphene.relay.Node.Field(MovieNode)
    movies = DjangoFilterConnectionField(MovieNode)

    def resolve_movie(self, info, **kwargs):
        return MovieNode.get_queryset(info)

    def resolve_movies(self, info, **kwargs):
        return MovieNode.get_queryset(info)
