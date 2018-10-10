from django.conf import settings
from django.utils.html import format_html
from reversion.admin import VersionAdmin

from cinemanio.api.helpers import global_id


class BaseAdmin(VersionAdmin):
    """
    Base admin model
    """
    def site(self, obj):
        link = f'{settings.FRONTEND_URL}{obj._meta.object_name.lower()}s/{global_id(obj)}/'
        return format_html('<a href="{}">link</a>', link)
