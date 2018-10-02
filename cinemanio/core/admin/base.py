from django.conf import settings
from django.utils.html import format_html
from graphql_relay.node.node import to_global_id
from reversion.admin import VersionAdmin


class BaseAdmin(VersionAdmin):
    """
    Base admin model
    """
    def site(self, obj):
        global_id = to_global_id(f'{obj._meta.object_name}Node', obj.id)
        link = f'{settings.FRONTEND_URL}{obj._meta.object_name.lower()}s/{global_id}/'
        return format_html('<a href="{}">link</a>', link)
