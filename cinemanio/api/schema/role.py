from graphene_django import DjangoObjectType

from cinemanio.api.utils import DjangoObjectTypeMixin
from cinemanio.core.models import Role


class RoleNode(DjangoObjectTypeMixin, DjangoObjectType):
    class Meta:
        model = Role
