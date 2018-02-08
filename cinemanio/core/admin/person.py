from django.contrib.admin import register
from reversion.admin import VersionAdmin

from cinemanio.core.models import Person
from cinemanio.core.admin.cast import CastInline


@register(Person)
class PersonAdmin(VersionAdmin):
    """
    Person admin model
    """
    list_display = ['id', 'first_name_en', 'last_name_en', 'first_name_ru', 'last_name_ru', 'date_birth', 'date_death']
    list_display_links = ('id',)
    search_fields = ('first_name', 'last_name', 'first_name_en', 'last_name_en', 'first_name_ru', 'last_name_ru')
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
