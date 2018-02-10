from graphene import relay
from graphene_django import DjangoObjectType

from cinemanio.core.models import Person


class PersonNode(DjangoObjectType):
    class Meta:
        model = Person
        filter_fields = ('country',)
        #     'title': ['exact', 'icontains', 'istartswith'],
        #     'company': ['exact'],
        #     'company__name': ['exact'],
        # }
        # filter_order_by = ['title', 'company__name']
        interfaces = (relay.Node,)
