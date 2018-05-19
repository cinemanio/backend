from django.contrib.admin import register
from reversion.admin import VersionAdmin

from cinemanio.images.models import Image, ImageLink


@register(Image)
class ImageAdmin(VersionAdmin):
    """
    Image admin model
    """


@register(ImageLink)
class ImageLinkAdmin(VersionAdmin):
    """
    ImageLink admin model
    """
