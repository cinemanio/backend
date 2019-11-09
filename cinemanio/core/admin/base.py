from django.conf import settings
from django.utils.html import format_html
from django.db.models import Count
from reversion.admin import VersionAdmin

from cinemanio.api.helpers import global_id


class BaseAdmin(VersionAdmin):
    """
    Base admin model
    """
    def view_on_site(self, obj):
        link = f'{settings.FRONTEND_URL}{obj._meta.object_name.lower()}s/{global_id(obj)}/'
        return link

    def view(self, obj):
        return format_html('<a href="{}">site</a>', self.view_on_site(obj))

    @property
    def roles_name(self):
        raise NotImplementedError()

    def roles_count(self, obj):
        return obj.roles_count

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(roles_count=Count(self.roles_name, distinct=True))
