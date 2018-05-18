import time
from urllib.request import urlopen
from urllib.parse import urlparse

import re
from django.core.files.base import ContentFile
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.translation import ugettext_lazy as _
from sorl.thumbnail import get_thumbnail
from sorl.thumbnail.fields import ImageField

from cinemanio.core.models import Movie, Person


class ImageWrongType(TypeError):
    pass


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

            # download url and save to image
            if 'http' not in url:
                url = 'http:' + url
            image.source = urlparse(url).netloc

            if image.source_type and image.source_id:
                name = f'{image.source_type}_{image.source_id}'
            else:
                name = str(time.time())

            f = urlopen(url)
            image.original.save(name, ContentFile(f.read()))

        return image

    # def upload(self, uploaded_image, **kwargs):
    #     """
    #     Handle file uploaded from user's PC
    #     """
    #     image = self.model()
    #     image.__dict__.update(kwargs)
    #
    #     image.original.name = image_original_upload_to(uploaded_image.name)
    #     file = image.get_original_path()
    #
    #     fd = open(file, 'wb+')
    #     for chunk in uploaded_image.chunks():
    #         fd.write(chunk)
    #     fd.close()
    #
    #     image.save()
    #     return image

    def get_or_download_for_object(self, url, object, **kwargs):
        """
        Try to get already downloaded or download image using self.download_for_object() method
        Return tuple with image_link instance and boolean flag equal True if image was downloaded
        """
        image = self.get_image_from_url(url=url)
        if image.id:
            image_link = ImageLink.objects.get_or_create(image=image, object_id=object.id,
                                                         content_type=ContentType.objects.get_for_model(object))[0]
            return image_link, False
        else:
            image_link = self.download_for_object(url, object, **kwargs)
            return image_link, True

    def download_for_object(self, url, object, **kwargs):
        """
        Download image and link it to object by ImageLink
        """
        image = self.download(url, **kwargs)
        image_link = ImageLink(image=image, object=object)
        image_link.save()
        return image_link

    # def upload_for_object(self, uploaded_image, object, **kwargs):
    #     """
    #     Upload image like self.upload() and link it to object by creating ImageLink connection
    #     """
    #     image = self.upload(uploaded_image, **kwargs)
    #     image_link = ImageLink(image=image, object=object)
    #     image_link.save()
    #     return image_link


def image_original_upload_to(filename=None):
    return 'images/%f.jpg' % time.time()


class Image(models.Model):
    """
    Image model
    """
    POSTER = 1
    PHOTO = 2

    TYPE_CHOICES = (
        (POSTER, _('Poster')),
        (PHOTO, _('Photo')),
    )

    SOURCE_REGEXP = {
        # http://st3.kinopoisk.ru/im/poster/1/1/1/kinopoisk.ru-Title-495390.jpg
        # //st.kp.yandex.net/im/poster/4/8/3/kinopoisk.ru-Les-amants-r_26_23233_3Bguliers-483294.jpg
        'kinopoisk': r'kinopoisk.ru\-.+\-(\d+)\.jpg$',
        # http://upload.wikimedia.org/wikipedia/commons/1/14/Francis_Ford_Coppola%28CannesPhotoCall%29_crop.jpg
        # http://upload.wikimedia.org/wikipedia/commons/9/9e/Francis_Ford_Coppola_2007_crop.jpg
        'wikicommons': r'^http://upload.wikimedia.org/wikipedia/commons/.+/([^/]+)$',
    }
    SOURCE_TYPE_CHOICES = [(k, k) for k in SOURCE_REGEXP.keys()]

    type = models.PositiveIntegerField(_('Type'), choices=TYPE_CHOICES, default=0, db_index=True)
    original = ImageField(_('Original'), upload_to='images')

    source = models.CharField(_('Source'), max_length=100, default='')
    source_type = models.CharField(_('Type of source'), choices=SOURCE_TYPE_CHOICES, max_length=20, null=True)
    source_id = models.CharField(_('Source ID'), max_length=300, null=True)

    objects = ImageManager()

    # card_dimensions = (100, 140)
    # detail_dimensions = (180, 240)
    # small_dimensions = (30, 40)

    class Meta:
        verbose_name = _('image')
        verbose_name_plural = _('images')
        get_latest_by = 'id'
        unique_together = ('source_type', 'source_id')
        ordering = ('-id',)

    # @property
    # def card(self):
    #     return self.get_thumbnail_url(self.card_dimensions)
    #
    # @property
    # def detail(self):
    #     return self.get_thumbnail_url(self.detail_dimensions)
    #
    # @property
    # def small(self):
    #     return self.get_thumbnail_url(self.small_dimensions)
    #
    # def get_thumbnail_url(self, dimensions):
    #     try:
    #         return settings.MEDIA_URL + get_thumbnail(self.original, 'x'.join(map(str, dimensions)),
    #                                                   crop='center',
    #                                                   upscale=True).name
    #     except OverflowError:
    #         return None
    #
    # def check_original(self):
    #     # TODO: если заливается через админскую форму, то пути не существует и можно заливать gif и png
    #     # нужно сделать проверку, чтобы только jpg
    #     file = self.get_original_path()
    #     if os.path.exists(file):
    #         try:
    #             im = PIL.Image.open(file)
    #             assert im.format == 'JPEG'
    #         except AssertionError:
    #             os.remove(file)
    #             raise ImageWrongType(_('Image file must be in jpeg format'))
    #
    # def get_original(self):
    #     return getattr(settings, 'MEDIA_URL') + self.original.name
    #
    # def get_original_path(self):
    #     return os.path.join(getattr(settings, 'MEDIA_ROOT'), self.original.name)
    #
    # def get_original_size(self):
    #     return os.path.getsize(self.get_original_path())
    #
    # def save(self, **kwargs):
    #     u"""
    #     Перед первым сохранением проверяем изображение на требования
    #     """
    #     if not self.id:
    #         self.check_original()
    #     super(Image, self).save(**kwargs)


class ImageLink(models.Model):
    """
    Image link to object model
    """
    image = models.ForeignKey(Image, related_name='links', on_delete=models.CASCADE)

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField(db_index=True)
    object = GenericForeignKey()

    class Meta:
        verbose_name = _('image link')
        verbose_name_plural = _('image links')
        unique_together = ('image', 'content_type', 'object_id')
        get_latest_by = 'id'

    def __repr__(self):
        return self.object


Movie.add_to_class('images', GenericRelation(ImageLink, verbose_name=_('Images')))
Person.add_to_class('images', GenericRelation(ImageLink, verbose_name=_('Images')))
