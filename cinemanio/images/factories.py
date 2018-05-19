import factory
from factory.django import DjangoModelFactory

from cinemanio.images.models import Image, ImageLink


class ImageFactory(DjangoModelFactory):
    class Meta:
        model = Image


class ImageLinkFactory(DjangoModelFactory):
    image = factory.SubFactory(ImageFactory)

    class Meta:
        model = ImageLink
