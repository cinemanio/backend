from django.contrib.admin import TabularInline

from cinemanio.core.admin import GenreAdmin
from cinemanio.sites.kinopoisk.models import KinopoiskGenre


class KinopoiskGenreInline(TabularInline):
    model = KinopoiskGenre


GenreAdmin.inlines = GenreAdmin.inlines + [KinopoiskGenreInline]
