from django.contrib import admin
from django.contrib.admin import register
from django.contrib.contenttypes.admin import GenericTabularInline
from reversion.admin import VersionAdmin

from cinemanio.core.admin.site import site
from cinemanio.core.admin import get_registered_admin_class
from cinemanio.core.models import Movie, Person
from cinemanio.images.models import Image, ImageLink
from cinemanio.images.forms import ImageInlineForm

MovieAdmin = get_registered_admin_class(Movie)
PersonAdmin = get_registered_admin_class(Person)
admin.site.unregister(Movie)
admin.site.unregister(Person)


@register(Image, site=site)
class ImageAdmin(VersionAdmin):
    """
    Image admin model
    """


@register(ImageLink, site=site)
class ImageLinkAdmin(VersionAdmin):
    """
    ImageLink admin model
    """


class ImagesInline(GenericTabularInline):
    classes = ('collapse', 'collapsed',)
    model = ImageLink
    form = ImageInlineForm
    extra = 0

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('image')

    def has_add_permission(self, request, obj=None):
        return False


@register(Movie, site=site)
class ImagesMovieAdmin(MovieAdmin):  # type: ignore
    inlines = MovieAdmin.inlines + (ImagesInline,)


@register(Person, site=site)
class ImagesPersonAdmin(PersonAdmin):  # type: ignore
    inlines = PersonAdmin.inlines + (ImagesInline,)
