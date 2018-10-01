from django.contrib import admin

from cinemanio.core.models import Cast
from cinemanio.core.admin.forms import CastInlineForm


class CastInline(admin.TabularInline):
    """
    Cast on Movie or career on Person pages in admin
    """

    model = Cast
    classes = ("collapse", "collapsed")
    autocomplete_fields = ["movie", "person"]
    form = CastInlineForm
    extra = 0

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("role", "person", "movie")
