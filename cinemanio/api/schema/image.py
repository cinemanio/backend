from graphene import String
from graphene_django import DjangoObjectType

from cinemanio.api.utils import DjangoObjectTypeMixin
from cinemanio.images.models import Image, ImageLink


class ImageNode(DjangoObjectTypeMixin, DjangoObjectType):
    full_card = String()
    short_card = String()
    detail = String()
    icon = String()

    class Meta:
        model = Image
        only_fields = ('type', 'original')
        use_connection = True


class ImageLinkNode(DjangoObjectTypeMixin, DjangoObjectType):
    class Meta:
        model = ImageLink
        filter_fields = ['image']
        only_fields = ('image',)
        use_connection = True
