import graphene
from graphene_django import DjangoObjectType

from cinemanio.api.utils import DjangoObjectTypeMixin
from cinemanio.core.models import Genre, Language, Country, Role

PROPERTY_FIELDS = ['id', 'name', 'name_en', 'name_ru']


class RoleNode(DjangoObjectTypeMixin, DjangoObjectType):
    class Meta:
        model = Role
        only_fields = PROPERTY_FIELDS


class GenreNode(DjangoObjectType):
    class Meta:
        model = Genre
        only_fields = PROPERTY_FIELDS


class LanguageNode(DjangoObjectType):
    class Meta:
        model = Language
        only_fields = PROPERTY_FIELDS


class CountryNode(DjangoObjectType):
    class Meta:
        model = Country
        only_fields = PROPERTY_FIELDS + ['code']


class PropertiesQuery:
    roles = graphene.List(RoleNode)
    genres = graphene.List(GenreNode)
    languages = graphene.List(LanguageNode)
    countries = graphene.List(CountryNode)

    def resolve_roles(self, *args, **kwargs):
        return Role.objects.all()

    def resolve_genres(self, *args, **kwargs):
        return Genre.objects.all()

    def resolve_languages(self, *args, **kwargs):
        return Language.objects.all()

    def resolve_countries(self, *args, **kwargs):
        return Country.objects.all()
