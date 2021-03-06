import graphene
from graphene_django import DjangoObjectType

from cinemanio.api.helpers import global_id
from cinemanio.api.utils import DjangoObjectTypeMixin
from cinemanio.core.models import Genre, Language, Country, Role
from cinemanio.core.utils.languages import translated_fields

PROPERTY_FIELDS = ('id',) + translated_fields('name')


class RoleNode(DjangoObjectTypeMixin, DjangoObjectType):
    class Meta:
        model = Role
        only_fields = PROPERTY_FIELDS

    def resolve_id(self, info):
        return global_id(Role(id=self.pk))


class GenreNode(DjangoObjectType):
    class Meta:
        model = Genre
        only_fields = PROPERTY_FIELDS

    def resolve_id(self, info):
        return global_id(Genre(id=self.pk))


class LanguageNode(DjangoObjectType):
    class Meta:
        model = Language
        only_fields = PROPERTY_FIELDS

    def resolve_id(self, info):
        return global_id(Language(id=self.pk))


class CountryNode(DjangoObjectType):
    class Meta:
        model = Country
        only_fields = PROPERTY_FIELDS + ('code',)

    def resolve_id(self, info):
        return global_id(Country(id=self.pk))


class PropertiesQuery:
    roles = graphene.List(RoleNode)
    genres = graphene.List(GenreNode)
    languages = graphene.List(LanguageNode)
    countries = graphene.List(CountryNode)

    def resolve_roles(self, _):
        return Role.objects.all()

    def resolve_genres(self, _):
        return Genre.objects.all()

    def resolve_languages(self, _):
        return Language.objects.all()

    def resolve_countries(self, _):
        return Country.objects.all()
