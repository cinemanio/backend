from django.conf import settings
from django.contrib.admin import register
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from graphql_relay.node.node import to_global_id
from reversion.admin import VersionAdmin

from cinemanio.core.admin.cast import CastInline
from cinemanio.core.forms import MovieForm
from cinemanio.core.models import Movie


@register(Movie)
class MovieAdmin(VersionAdmin):
    """
    Movie admin model
    """
    list_display = ['id', 'year', 'title_en', 'title_ru', 'site']
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

    def site(self, obj):
        from cinemanio.api.schema.movie import MovieNode
        global_id = to_global_id(MovieNode._meta.name, obj.id)
        return mark_safe(f'<a href="{settings.FRONTEND_URL}movies/{global_id}/">link</a>')
