from graphene_django import DjangoObjectType

from cinemanio.api.utils import DjangoObjectTypeMixin
from cinemanio.core.models import Cast


class CastNode(DjangoObjectTypeMixin, DjangoObjectType):
    class Meta:
        model = Cast
        filter_fields = ["role"]
        use_connection = True
