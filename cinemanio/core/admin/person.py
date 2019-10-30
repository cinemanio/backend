from django.contrib.admin import register

from cinemanio.core.admin.site import site
from cinemanio.core.admin.base import BaseAdmin
from cinemanio.core.admin.cast import CastInline
from cinemanio.core.models import Person


@register(Person, site=site)
class PersonAdmin(BaseAdmin):
    """
    Person admin model
    """
    list_display = ['id', 'first_name_en', 'last_name_en', 'first_name_ru', 'last_name_ru', 'date_birth', 'date_death',
                    'view']
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
