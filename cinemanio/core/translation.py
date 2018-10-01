from modeltranslation.translator import register, TranslationOptions

from cinemanio.core.models import Cast, Genre, Language, Country, Role, Movie, Person


class OptionsMixin:
    required_languages = ("en",)


@register(Cast)
class CastTranslationOptions(TranslationOptions, OptionsMixin):
    fields = ("name",)


@register(Genre)
@register(Language)
@register(Country)
@register(Role)
class PropertyTranslationOptions(TranslationOptions, OptionsMixin):
    fields = ("name",)


@register(Movie)
class MovieTranslationOptions(TranslationOptions, OptionsMixin):
    fields = ("title",)


@register(Person)
class PersonTranslationOptions(TranslationOptions, OptionsMixin):
    fields = ("first_name", "last_name")
