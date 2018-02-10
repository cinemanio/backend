from graphene import relay
from graphene_django import DjangoObjectType

from cinemanio.core.models import Movie


class MovieNode(DjangoObjectType):
    class Meta:
        model = Movie
        filter_fields = ['year', 'genres', 'countries', 'languages']
        # filter_order_by = ['name']
        interfaces = (relay.Node,)
