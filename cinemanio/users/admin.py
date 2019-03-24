from django.contrib.admin import register
from django.contrib.auth.admin import UserAdmin

from cinemanio.users.models import User


@register(User)
class UserAdmin(UserAdmin):
    """
    User admin model
    """
    pass
