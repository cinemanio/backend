from graphene import relay, String, Field
from graphene_django import DjangoObjectType

from cinemanio.api.schema.mixins import ImagesMixin, RelationsMixin, WikipediaMixin
from cinemanio.api.schema.cast import CastNode
from cinemanio.api.filtersets import PersonFilterSet
from cinemanio.api.utils import DjangoObjectTypeMixin, DjangoFilterConnectionField, CountableConnectionBase
from cinemanio.api.schema.image import ImageNode
from cinemanio.core.models import Person
from cinemanio.images.models import ImageType


class PersonNode(RelationsMixin, DjangoObjectTypeMixin, DjangoObjectType, ImagesMixin, WikipediaMixin):
    career = DjangoFilterConnectionField(CastNode)
    photo = Field(ImageNode)
    name = String()
    name_en = String()
    name_ru = String()

    class Meta:
        model = Person
        only_fields = (
            'id',
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

    def resolve_photo(self, _, **__):
        return PersonNode.get_random_image(self, ImageType.PHOTO)


class PersonQuery:
    person = relay.Node.Field(PersonNode)
    persons = DjangoFilterConnectionField(PersonNode, filterset_class=PersonFilterSet)

    def resolve_person(self, info):
        return PersonNode.get_queryset(info)

    def resolve_persons(self, info, **_):
        return PersonNode.get_queryset(info)
