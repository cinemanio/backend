import graphene
from graphene import relay
from graphene_django import DjangoObjectType

from cinemanio.api.utils import DjangoObjectTypeMixin, DjangoFilterConnectionField
from cinemanio.core.models import Person


class PersonNode(DjangoObjectTypeMixin, DjangoObjectType):

    class Meta:
        model = Person
        filter_fields = {
            'country': ['exact'],
            'date_birth': ['year'],
        }
        interfaces = (relay.Node,)


class PersonQuery:
    person = graphene.relay.Node.Field(PersonNode)
    persons = DjangoFilterConnectionField(PersonNode)

    def resolve_person(self, info, **kwargs):
        return PersonNode.get_queryset(info)

    def resolve_persons(self, info, **kwargs):
        return PersonNode.get_queryset(info)
