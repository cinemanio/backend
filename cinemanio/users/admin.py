from django.contrib.admin import register
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from cinemanio.core.admin.site import site
from cinemanio.users.models import User


@register(User, site=site)
class UserAdmin(BaseUserAdmin):
    """
    User admin model
    """
    pass
