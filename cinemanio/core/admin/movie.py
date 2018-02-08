from django.contrib.admin import register
from django.utils.translation import ugettext_lazy as _
from reversion.admin import VersionAdmin

from cinemanio.core.forms import MovieForm
from cinemanio.core.models import Movie
from cinemanio.core.admin.cast import CastInline


@register(Movie)
class MovieAdmin(VersionAdmin):
    """
    Movie admin model
    """
    list_display = ['id', 'year', 'title_en', 'title_ru']
    list_display_links = ('id',)
    search_fields = ('title', 'title_ru', 'title_en')
    autocomplete_fields = ['sequel_for', 'prequel_for', 'remake_for']
    form = MovieForm
    inlines = [CastInline]
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
        (_('Genres, languages and countries'), {
            'classes': ('collapse', 'collapsed'),
            'fields': ('genres', 'languages', 'countries'),
        }),
    )
