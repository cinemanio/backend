from graphene_django import DjangoObjectType

from cinemanio.core.models import Genre, Language, Country


class GenreNode(DjangoObjectType):
    class Meta:
        model = Genre


class LanguageNode(DjangoObjectType):
    class Meta:
        model = Language


class CountryNode(DjangoObjectType):
    class Meta:
        model = Country
