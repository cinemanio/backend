from django.contrib.contenttypes.models import ContentType

from cinemanio.api.schema.image import ImageLinkNode
from cinemanio.api.utils import DjangoFilterConnectionField


class ImagesMixin:
    images = DjangoFilterConnectionField(ImageLinkNode)

    def resolve_images(self, info, **_):
        return ImageLinkNode.get_queryset(info).filter(object_id=self.pk,
                                                       content_type=ContentType.objects.get_for_model(self))

    def get_random_image(self, image_type):
        image_link = self.images.filter(image__type=image_type).order_by('?').first()
        return image_link.image if image_link else None
