from typing import Tuple

from django.contrib.admin import register
from reversion.admin import VersionAdmin

from cinemanio.core.admin.site import site
from cinemanio.core.models import Genre, Country, Language
from cinemanio.core.utils.languages import translated_fields

Param = Tuple[str, ...]

names = translated_fields('name', with_base=True)


class PropAdminBase(VersionAdmin):
    """Base admin model for props"""
    list_display: Param = ('id',) + names + ('imdb_name', 'kinopoisk_name')
    list_display_links: Param = ('id',)
    list_editable: Param = names
    ordering: Param = ('id',)

    def imdb_name(self, obj):
        return obj.imdb.name

    imdb_name.admin_order_field = 'imdb__name'  # type: ignore

    def kinopoisk_name(self, obj):
        return obj.kinopoisk.name

    kinopoisk_name.admin_order_field = 'kinopoisk__name'  # type: ignore

    def get_queryset(self, request):
        return self.model.objects.select_related('imdb', 'kinopoisk')


@register(Genre, site=site)
class GenreAdmin(PropAdminBase):
    """
    Genre admin model
    """


@register(Country, site=site)
class CountryAdmin(PropAdminBase):
    """
    Country admin model
    """
    list_display = ('id', 'code') + names + ('imdb_name', 'kinopoisk_name')
    list_editable = names + ('code',)


@register(Language, site=site)
class LanguageAdmin(PropAdminBase):
    """
    Language admin model
    """
    list_display = ('id',) + names + ('imdb_name',)

    def get_queryset(self, request):
        return self.model.objects.select_related('imdb')
