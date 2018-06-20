from graphene import relay, String
from graphene_django import DjangoObjectType

from cinemanio.api.schema.cast import CastNode
from cinemanio.api.filtersets import PersonFilterSet
from cinemanio.api.utils import DjangoObjectTypeMixin, DjangoFilterConnectionField, CountableConnectionBase
from cinemanio.core.models import Person


class PersonNode(DjangoObjectTypeMixin, DjangoObjectType):
    career = DjangoFilterConnectionField(CastNode)
    name = String()
    name_en = String()
    name_ru = String()

    class Meta:
        model = Person
        only_fields = (
            'id',
            'first_name', 'last_name',
            'first_name_en', 'last_name_en',
            'first_name_ru', 'last_name_ru',
            'gender', 'date_birth', 'date_death',
            'country', 'roles',
            'imdb', 'kinopoisk',
        )
        interfaces = (relay.Node,)
        connection_class = CountableConnectionBase

    def resolve_career(self, info, **_):
        return CastNode.get_queryset(info).filter(person=self)


class PersonQuery:
    person = relay.Node.Field(PersonNode)
    persons = DjangoFilterConnectionField(PersonNode, filterset_class=PersonFilterSet)

    def resolve_person(self, info):
        return PersonNode.get_queryset(info)

    def resolve_persons(self, info, **_):
        return PersonNode.get_queryset(info)
