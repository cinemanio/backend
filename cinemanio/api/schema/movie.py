import graphene
from graphene import relay
from graphene_django import DjangoObjectType

from cinemanio.api.utils import DjangoObjectTypeMixin, DjangoFilterConnectionField
from cinemanio.core.models import Movie


class MovieNode(DjangoObjectTypeMixin, DjangoObjectType):
    class Meta:
        model = Movie
        filter_fields = ['year', 'genres', 'countries', 'languages']
        interfaces = (relay.Node,)

    def resolve_cast(self, *args, **kwargs):
        return self.cast.select_related('person', 'role')

    def resolve_imdb(self, *args, **kwargs):
        try:
            return self.imdb
        except AttributeError:
            return None

    def resolve_kinopoisk(self, *args, **kwargs):
        try:
            return self.kinopoisk
        except AttributeError:
            return None


class MovieQuery:
    movie = graphene.relay.Node.Field(MovieNode)
    movies = DjangoFilterConnectionField(MovieNode)

    def resolve_movie(self, info, **kwargs):
        return MovieNode.get_queryset(info)

    def resolve_movies(self, info, **kwargs):
        return MovieNode.get_queryset(info)
