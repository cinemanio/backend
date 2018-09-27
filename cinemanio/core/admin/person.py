from django.conf import settings
from django.contrib.admin import register
from django.utils.safestring import mark_safe
from graphql_relay.node.node import to_global_id
from reversion.admin import VersionAdmin

from cinemanio.core.admin.cast import CastInline
from cinemanio.core.models import Person


@register(Person)
class PersonAdmin(VersionAdmin):
    """
    Person admin model
    """
    list_display = ['id', 'first_name_en', 'last_name_en', 'first_name_ru', 'last_name_ru', 'date_birth', 'date_death',
                    'site']
    list_display_links = ['id']
    search_fields = ['first_name', 'last_name', 'first_name_en', 'last_name_en', 'first_name_ru', 'last_name_ru']
    inlines = [CastInline]
    fieldsets = (
        (None, {
            'fields': (
                ('first_name', 'last_name', 'gender'),
                ('first_name_en', 'last_name_en'),
                ('first_name_ru', 'last_name_ru'),
                ('country', 'date_birth', 'date_death'),
            )
        }),
    )

    def site(self, obj):
        from cinemanio.api.schema.person import PersonNode
        global_id = to_global_id(PersonNode._meta.name, obj.id)
        return mark_safe(f'<a href="{settings.FRONTEND_URL}persons/{global_id}/">link</a>')
