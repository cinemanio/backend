from graphene_django import DjangoObjectType

from cinemanio.core.models import Genre, Language, Country


class GenreType(DjangoObjectType):
    class Meta:
        model = Genre


class LanguageType(DjangoObjectType):
    class Meta:
        model = Language


class CountryType(DjangoObjectType):
    class Meta:
        model = Country
