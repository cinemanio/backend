import graphene
from graphene import relay, Field
from graphene_django import DjangoObjectType

from cinemanio.api.schema.mixins import ImagesMixin
from cinemanio.api.schema.cast import CastNode
from cinemanio.api.filtersets import MovieFilterSet
from cinemanio.api.utils import DjangoObjectTypeMixin, DjangoFilterConnectionField, CountableConnectionBase
from cinemanio.api.schema.image import ImageNode
from cinemanio.core.models import Movie
from cinemanio.images.models import ImageType


class MovieNode(DjangoObjectTypeMixin, DjangoObjectType, ImagesMixin):
    cast = DjangoFilterConnectionField(CastNode)
    poster = Field(ImageNode)

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
        interfaces = (relay.Node,)
        connection_class = CountableConnectionBase

    def resolve_cast(self, info, *args, **kwargs):
        return CastNode.get_queryset(info).filter(movie=self)

    def resolve_poster(self, info, *args, **kwargs):
        return MovieNode.get_random_image(self, ImageType.POSTER)


class MovieQuery:
    movie = graphene.relay.Node.Field(MovieNode)
    movies = DjangoFilterConnectionField(MovieNode, filterset_class=MovieFilterSet)

    def resolve_movie(self, info, **kwargs):
        return MovieNode.get_queryset(info)

    def resolve_movies(self, info, **kwargs):
        return MovieNode.get_queryset(info)
