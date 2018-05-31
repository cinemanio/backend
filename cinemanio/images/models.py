import time
from urllib.parse import urlparse
from urllib.request import urlopen

import re
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.core.files.base import ContentFile
from django.db import models
from django.utils.translation import ugettext_lazy as _
from sorl.thumbnail.fields import ImageField
from sorl.thumbnail import get_thumbnail

from cinemanio.core.models import Movie, Person


class ImageWrongType(Exception):
    pass


class ImageLinkManager(models.Manager):
    def get_or_download(self, url, **kwargs):
        """
        Try to get already downloaded or download image using self.download() method
        Return tuple with image_link instance and boolean flag equal True if image was downloaded
        """
        assert self.instance, "Manager method should be called: instance.images.get_or_download()"

        image = Image.objects.get_image_from_url(url=url)
        if image.id:
            image_link = self.get_or_create(image=image, object_id=self.instance.id,
                                            content_type=ContentType.objects.get_for_model(self.instance))[0]
            return image_link, False
        else:
            image_link = self.download(url, **kwargs)
            return image_link, True

    def download(self, url, **kwargs):
        """
        Download image and link it to self.instance
        """
        assert self.instance, "Manager method should be called: instance.images.download()"

        image = Image.objects.download(url, **kwargs)
        image_link = self.model(image=image, object=self.instance)
        image_link.save()
        return image_link


class ImageManager(models.Manager):
    def get_image_from_url(self, url=None):
        """
        Check if image has ever been downloaded before and return if found, otherwise initialize new
        """
        image = self.model()

        if url:
            for type, regexp in self.model.SOURCE_REGEXP.items():
                id = re.compile(regexp).findall(url)
                if id:
                    try:
                        return self.get(source_type=type, source_id=id[0])
                    except self.model.DoesNotExist:
                        image.source_id = id[0]
                        image.source_type = type

        return image

    def download(self, url, **kwargs):
        """
        Download image from URL save and return it
        """
        image = self.get_image_from_url(url)
        if not image.id:
            image.__dict__.update(kwargs)
            if 'http' not in url:
                url = 'http:' + url
            image.source = urlparse(url).netloc
            image.download(url)
        return image


class Image(models.Model):
    """
    Image model
    """
    POSTER = 1
    PHOTO = 2

    TYPE_CHOICES = [
        (POSTER, _('Poster')),
        (PHOTO, _('Photo')),
    ]

    SOURCE_REGEXP = {
        # http://st3.kinopoisk.ru/im/poster/1/1/1/kinopoisk.ru-Title-495390.jpg
        # //st.kp.yandex.net/im/poster/4/8/3/kinopoisk.ru-Les-amants-r_26_23233_3Bguliers-483294.jpg
        'kinopoisk': r'kinopoisk.ru\-.+\-(\d+)\.jpg$',
        # http://upload.wikimedia.org/wikipedia/commons/1/14/Francis_Ford_Coppola%28CannesPhotoCall%29_crop.jpg
        # http://upload.wikimedia.org/wikipedia/commons/9/9e/Francis_Ford_Coppola_2007_crop.jpg
        'wikicommons': r'^http://upload.wikimedia.org/wikipedia/commons/.+/([^/]+)$',
    }
    SOURCE_TYPE_CHOICES = [(k, k) for k in SOURCE_REGEXP.keys()]

    type = models.PositiveIntegerField(_('Type'), choices=TYPE_CHOICES, null=True, db_index=True)
    original = ImageField(_('Original'), upload_to='images')

    source = models.CharField(_('Source'), max_length=100, default='', blank=True)
    source_type = models.CharField(_('Type of source'), choices=SOURCE_TYPE_CHOICES, max_length=20, null=True,
                                   blank=True)
    source_id = models.CharField(_('Source ID'), max_length=300, null=True, blank=True)

    objects = ImageManager()

    class Meta:
        verbose_name = _('image')
        verbose_name_plural = _('images')
        get_latest_by = 'id'
        unique_together = ('source_type', 'source_id')
        ordering = ('-id',)

    DETAIL_SIZE = (180, 255)
    FULL_CARD_SIZE = (100, 140)
    SHORT_CARD_SIZE = (42, 58)
    ICON_SIZE = (30, 40)

    def get_thumbnail(self, width, height):
        return get_thumbnail(self.original, f'{width}x{height}', crop='center', upscale=True)

    def download(self, url):
        """
        Download image from url and save it into ImageField
        """
        name = f'{time.time()}.jpg'
        f = urlopen(url)
        self.original.save(name, ContentFile(f.read()))


class ImageLink(models.Model):
    """
    Image link to object model
    """
    image = models.ForeignKey(Image, related_name='links', on_delete=models.CASCADE)

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField(db_index=True)
    object = GenericForeignKey()

    objects = ImageLinkManager()

    class Meta:
        verbose_name = _('image link')
        verbose_name_plural = _('image links')
        unique_together = ('image', 'content_type', 'object_id')
        get_latest_by = 'id'

    def __repr__(self):
        return f'ImageLink: {self.object}'


Movie.add_to_class('images', GenericRelation(ImageLink, verbose_name=_('Images')))
Person.add_to_class('images', GenericRelation(ImageLink, verbose_name=_('Images')))
