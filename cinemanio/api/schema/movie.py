import graphene
from graphene import relay
from graphene_django import DjangoObjectType

from cinemanio.api.utils import DjangoObjectTypeMixin, DjangoFilterConnectionField, CountableConnectionBase
from cinemanio.api.schema.cast import CastNode
from cinemanio.core.models import Movie


class MovieNode(DjangoObjectTypeMixin, DjangoObjectType):
    cast = DjangoFilterConnectionField(CastNode)

    class Meta:
        model = Movie
        only_fields = (
            'id',
            'title', 'title_en', 'title_ru',
            'year', 'runtime', 'award',
            'genres', 'countries', 'languages',
            'sequel_for', 'prequel_for', 'remake_for',
            'imdb', 'kinopoisk',
        )
        filter_fields = {
            'year': ['exact'],
            'genres': ['exact', 'in'],
            'countries': ['exact', 'in'],
            'languages': ['exact', 'in'],
        }
        interfaces = (relay.Node,)
        connection_class = CountableConnectionBase

    def resolve_cast(self, info, *args, **kwargs):
        return CastNode.get_queryset(info).filter(movie=self)


class MovieQuery:
    movie = graphene.relay.Node.Field(MovieNode)
    movies = DjangoFilterConnectionField(MovieNode)

    def resolve_movie(self, info, **kwargs):
        return MovieNode.get_queryset(info)

    def resolve_movies(self, info, **kwargs):
        return MovieNode.get_queryset(info)
