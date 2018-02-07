from django.contrib.admin import register
from django.utils.translation import ugettext_lazy as _
from reversion.admin import VersionAdmin

from cinemanio.core.forms import MovieForm
from cinemanio.core.models import Movie


@register(Movie)
class MovieAdmin(VersionAdmin):
    """
    Movie admin model
    """
    list_display = ('id', 'year', 'title')
    list_display_links = ('title',)
    search_fields = ('title', 'title_ru', 'title_en')
    form = MovieForm
    fieldsets = (
        (None, {
            'fields': (
                ('title', 'year',),
                ('title_en', 'title_ru'),
                ('runtime', 'novel_isbn'),
            ),
        }),
        (_('Associations with other movies'), {
            'classes': ('collapse', 'collapsed'),
            'fields': ('sequel_for', 'prequel_for', 'remake_for'),
        }),
        (_('Types, genres, languages and countries'), {
            'classes': ('collapse', 'collapsed'),
            'fields': ('types', 'genres', 'languages', 'countries'),
        }),
    )
