from django.conf import settings
from django.utils.html import format_html
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
