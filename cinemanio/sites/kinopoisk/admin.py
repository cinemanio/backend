from django.contrib.admin import TabularInline

from cinemanio.core.admin import GenreAdmin
from cinemanio.sites.kinopoisk.models import KinopoiskGenre
from cinemanio.sites.kinopoisk import signals  # noqa


class KinopoiskGenreInline(TabularInline):
    model = KinopoiskGenre


GenreAdmin.inlines = GenreAdmin.inlines + [KinopoiskGenreInline]
