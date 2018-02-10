import graphene
from graphene import relay
from graphene_django import DjangoObjectType

from cinemanio.api.utils import DjangoFilterConnectionField
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


class PersonQuery:
    person = graphene.relay.Node.Field(PersonNode)
    persons = DjangoFilterConnectionField(PersonNode)

    def resolve_person(self, info, **kwargs):
        return PersonNode.get_queryset(info)

    def resolve_persons(self, info, **kwargs):
        return PersonNode.get_queryset(info)
