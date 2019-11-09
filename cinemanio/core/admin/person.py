from django.contrib.admin import register

from cinemanio.core.admin.site import site
from cinemanio.core.admin.base import BaseAdmin
from cinemanio.core.admin.cast import CastInline
from cinemanio.core.models import Person
from cinemanio.core.utils.languages import translated_fields


@register(Person, site=site)
class PersonAdmin(BaseAdmin):
    """
    Person admin model
    """
    roles_name = 'career'
    list_display = ('id',) + translated_fields('first_name', 'last_name') + ('date_birth', 'date_death',
                                                                             'roles_count', 'view')
    list_display_links = ('id',)
    search_fields = translated_fields('first_name', 'last_name', with_base=True)
    inlines = (CastInline,)
    fieldsets = (
        (None, {
            'fields': (
                ('first_name', 'last_name', 'gender'),
                translated_fields('first_name', 'last_name'),
                ('country', 'date_birth', 'date_death'),
            )
        }),
    )
