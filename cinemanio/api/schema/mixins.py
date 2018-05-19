from django.contrib.contenttypes.models import ContentType

from cinemanio.api.schema.image import ImageLinkNode
from cinemanio.api.utils import DjangoFilterConnectionField


class ImagesMixin:
    images = DjangoFilterConnectionField(ImageLinkNode)

    def resolve_images(self, info, *args, **kwargs):
        return ImageLinkNode.get_queryset(info).filter(object_id=self.pk,
                                                       content_type=ContentType.objects.get_for_model(self))
