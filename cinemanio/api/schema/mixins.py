from django.contrib.contenttypes.models import ContentType

from cinemanio.api.schema.image import ImageLinkNode
from cinemanio.api.utils import DjangoFilterConnectionField


class ImagesMixin:
    images = DjangoFilterConnectionField(ImageLinkNode)

    def resolve_images(self, info, *args, **kwargs):
        return ImageLinkNode.get_queryset(info).filter(object_id=self.pk,
                                                       content_type=ContentType.objects.get_for_model(self))

    def get_random_image(self, image_type):
        image_link = self.images.filter(image__type=image_type).order_by('?').first()
        return image_link.image if image_link else None


import graphene
from django.core.exceptions import ObjectDoesNotExist
from cinemanio.api.schema.relations import RelationNode, RelationCountNode


class RelationsMixin:
    relation = graphene.Field(RelationNode)
    relations_count = graphene.Field(RelationCountNode)

    def resolve_relation(self, info, *args, **kwargs):
        user = info.context.user
        if not user:
            return None

        try:
            return self.relations.get(user=user)
        except ObjectDoesNotExist:
            import ipdb; ipdb.set_trace()

    def resolve_relations_count(self, info, *args, **kwargs):
        return self.relations_count
