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

    def resolve_original(self, *args, **kwargs):
        return self.original.url

    def resolve_full_card(self, *args, **kwargs):
        return self.get_thumbnail(*Image.FULL_CARD_SIZE).url

    def resolve_short_card(self, *args, **kwargs):
        return self.get_thumbnail(*Image.SHORT_CARD_SIZE).url

    def resolve_detail(self, *args, **kwargs):
        return self.get_thumbnail(*Image.DETAIL_SIZE).url

    def resolve_icon(self, *args, **kwargs):
        return self.get_thumbnail(*Image.ICON_SIZE).url


class ImageLinkNode(DjangoObjectTypeMixin, DjangoObjectType):
    class Meta:
        model = ImageLink
        filter_fields = ['image']
        only_fields = ('image',)
        use_connection = True
