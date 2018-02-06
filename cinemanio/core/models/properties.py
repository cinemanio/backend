from caching.base import CachingManager, CachingMixin
from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _


class CachingManagerNew(CachingManager):
    def get_queryset(self):
        qs = super(CachingManagerNew, self).get_queryset()
        qs.timeout = getattr(settings, 'CACHING_QUERYSET_TIMEOUT', 0)
        return qs


class PropertyModel(CachingMixin, models.Model):
    """
    Abstract base model for property models (Genre, Type, Language, Country, Role)
    """
    name = models.CharField(_('Name'), max_length=50, default='')

    objects = CachingManagerNew()

    class Meta:
        abstract = True
        ordering = ('name',)

    def __repr__(self):
        return self.name

    def __str__(self):
        return self.name


class Genre(PropertyModel):
    """
    Movie genre
    """

    class Meta(PropertyModel.Meta):
        verbose_name = _('genre')
        verbose_name_plural = _('genres')


class Language(PropertyModel):
    """
    Movie language
    """

    class Meta(PropertyModel.Meta):
        verbose_name = _('language')
        verbose_name_plural = _('languages')


class Country(PropertyModel):
    """
    Country of movie or person
    """

    class Meta(PropertyModel.Meta):
        verbose_name = _('country')
        verbose_name_plural = _('countries')


class Type(PropertyModel):
    """
    Movie type
    """
    DOCUMENTARY_ID = 7
    ANIMATION_ID = 5
    SHORT_ID = 5
    MUSICAL_ID = 12
    BLACK_AND_WHITE_ID = 14
    SILENT_ID = 1
    SERIES_ID = 2

    class Meta(PropertyModel.Meta):
        verbose_name = _('type')
        verbose_name_plural = _('types')
