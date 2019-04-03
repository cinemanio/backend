from django.contrib.admin import register
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from cinemanio.users.models import User


@register(User)
class UserAdmin(BaseUserAdmin):
    """
    User admin model
    """
    pass
