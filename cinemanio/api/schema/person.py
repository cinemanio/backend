import graphene
from graphene import relay
from graphene_django import DjangoObjectType

from cinemanio.api.utils import DjangoObjectTypeMixin, DjangoFilterConnectionField
from cinemanio.api.schema.cast import CastNode
from cinemanio.core.models import Person


class PersonNode(DjangoObjectTypeMixin, DjangoObjectType):
    career = DjangoFilterConnectionField(CastNode)

    class Meta:
        model = Person
        only_fields = (
            'id', 'first_name', 'last_name',
            'gender', 'date_birth', 'date_death', 'country',
            'imdb', 'kinopoisk',
        )
        filter_fields = {
            'country': ['exact'],
            'date_birth': ['year'],
        }
        interfaces = (relay.Node,)

    def resolve_career(self, info, *args, **kwargs):
        return CastNode.get_queryset(info).filter(person=self)


class PersonQuery:
    person = graphene.relay.Node.Field(PersonNode)
    persons = DjangoFilterConnectionField(PersonNode)

    def resolve_person(self, info, **kwargs):
        return PersonNode.get_queryset(info)

    def resolve_persons(self, info, **kwargs):
        return PersonNode.get_queryset(info)
