from modeltranslation.translator import register, TranslationOptions

from cinemanio.core.models import Cast, Genre, Type, Language, Country, Role, Movie, Person


class OptionsMixin:
    required_languages = ('en', )


@register(Cast)
class CastTranslationOptions(TranslationOptions, OptionsMixin):
    fields = ('name',)


@register(Genre)
@register(Type)
@register(Language)
@register(Country)
@register(Role)
class PropertyTranslationOptions(TranslationOptions, OptionsMixin):
    fields = ('name',)


@register(Movie)
class MovieTranslationOptions(TranslationOptions, OptionsMixin):
    fields = ('title',)


@register(Person)
class MovieTranslationOptions(TranslationOptions, OptionsMixin):
    fields = ('first_name', 'last_name')
