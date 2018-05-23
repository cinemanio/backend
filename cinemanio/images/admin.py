from django.contrib import admin
from django.contrib.admin import register
from django.contrib.contenttypes.admin import GenericTabularInline
from reversion.admin import VersionAdmin

from cinemanio.core.models import Movie, Person
from cinemanio.images.models import Image, ImageLink
from cinemanio.images.forms import ImageInlineForm

MovieAdmin = admin.site._registry[Movie].__class__
PersonAdmin = admin.site._registry[Person].__class__
admin.site.unregister(Movie)
admin.site.unregister(Person)


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


class ImagesInline(GenericTabularInline):
    classes = ('collapse', 'collapsed',)
    model = ImageLink
    raw_id_fields = ('image',)
    # readonly_fields = ('image',)
    form = ImageInlineForm
    extra = 0

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('image')


@register(Movie)
class ImagesMovieAdmin(MovieAdmin):
    inlines = MovieAdmin.inlines + [ImagesInline]


@register(Person)
class ImagesPersonAdmin(PersonAdmin):
    inlines = PersonAdmin.inlines + [ImagesInline]
