from django.contrib.admin import register
from reversion.admin import VersionAdmin

from cinemanio.core.models import Genre, Country, Language


class PropAdminBase(VersionAdmin):
    """Base admin model for props"""
    list_display = ('id', 'name', 'name_ru', 'name_en', 'imdb_name', 'kinopoisk_name')
    list_display_links = ('id',)
    list_editable = ('name', 'name_ru', 'name_en')
    ordering = ('id',)

    def imdb_name(self, obj):
        return obj.imdb.name

    imdb_name.admin_order_field = 'imdb__name'

    def kinopoisk_name(self, obj):
        return obj.kinopoisk.name

    kinopoisk_name.admin_order_field = 'kinopoisk__name'

    def get_queryset(self, request):
        return self.model.objects.select_related('imdb', 'kinopoisk')


@register(Genre)
class GenreAdmin(PropAdminBase):
    """
    Genre admin model
    """


@register(Country)
class CountryAdmin(PropAdminBase):
    """
    Country admin model
    """
    list_display = ('id', 'code', 'name', 'name_ru', 'name_en', 'imdb_name', 'kinopoisk_name')
    list_editable = ('name', 'name_ru', 'name_en', 'code')


@register(Language)
class LanguageAdmin(PropAdminBase):
    """
    Language admin model
    """
    list_display = ('id', 'name', 'name_ru', 'name_en', 'imdb_name')

    def get_queryset(self, request):
        return self.model.objects.select_related('imdb')
