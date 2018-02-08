from django.contrib import admin

from cinemanio.core.models import Cast


class CastInline(admin.TabularInline):
    """
    Cast on Movie or career on Person pages in admin
    """
    model = Cast
    classes = ('collapse', 'collapsed',)
    autocomplete_fields = ['movie', 'person']
    extra = 0
