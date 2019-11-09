from django.contrib.admin import register
from django.utils.translation import ugettext_lazy as _

from cinemanio.core.admin.site import site
from cinemanio.core.admin.base import BaseAdmin
from cinemanio.core.admin.cast import CastInline
from cinemanio.core.forms import MovieForm
from cinemanio.core.models import Movie


@register(Movie, site=site)
class MovieAdmin(BaseAdmin):
    """
    Movie admin model
    """
    roles_name = 'cast'
    list_display = ('id', 'year', 'title_en', 'title_ru', 'roles_count', 'view')
    list_display_links = ['id']
    autocomplete_fields = ['sequel_for', 'prequel_for', 'remake_for']
    search_fields = ['title', 'title_ru', 'title_en']
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
