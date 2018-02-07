from django.contrib.admin import TabularInline

from cinemanio.core.admin import GenreAdmin
from cinemanio.sites.imdb.models import ImdbGenre


class ImdbGenreInline(TabularInline):
    model = ImdbGenre


GenreAdmin.inlines = GenreAdmin.inlines + [ImdbGenreInline]
