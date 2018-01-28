from caching.base import CachingManager, CachingMixin
from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _

from cinemanio.core.models.person import (
    ACTOR_ID,
    DIRECTOR_ID,
    SCENARIST_ID,
    OPERATOR_ID,
    COMPOSER_ID,
    AUTHOR_ID,
    MUSICIAN_ID,
)


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


class PropertyImdbModel(PropertyModel):
    """
    Abstract base model for property models with imdb connection (Genre, Language, Country)
    """
    imdb_id = models.CharField(_('IMDb name'), max_length=50, null=True, unique=True, blank=True)

    class Meta:
        abstract = True


class Genre(PropertyImdbModel):
    """
    Movie genre
    """

    class Meta(PropertyModel.Meta):
        verbose_name = _('genre')
        verbose_name_plural = _('genres')


class Language(PropertyImdbModel):
    """
    Movie language
    """

    class Meta(PropertyModel.Meta):
        verbose_name = _('language')
        verbose_name_plural = _('languages')


class Country(PropertyImdbModel):
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

    class Meta(PropertyModel.Meta):
        verbose_name = _('type')
        verbose_name_plural = _('types')


class RoleManager(models.Manager):
    def get_actor(self):
        return self.get(id=ACTOR_ID)

    def get_director(self):
        return self.get(id=DIRECTOR_ID)

    def get_author(self):
        return self.get(id=AUTHOR_ID)

    def get_operator(self):
        return self.get(id=OPERATOR_ID)

    def get_scenarist(self):
        return self.get(id=SCENARIST_ID)

    def get_composer(self):
        return self.get(id=COMPOSER_ID)


class Role(PropertyModel):
    """
    Role Model
    """
    objects = RoleManager()

    class Meta(PropertyModel.Meta):
        verbose_name = _('role')
        verbose_name_plural = _('roles')

    def get_name(self, gender=1):
        # TODO: conversion Actor -> Actress depends on gender
        return self.name

    def is_actor(self):
        return self.id == ACTOR_ID

    def is_director(self):
        return self.id == DIRECTOR_ID

    def is_author(self):
        return self.id == AUTHOR_ID

    def is_operator(self):
        return self.id == OPERATOR_ID

    def is_scenarist(self):
        return self.id == SCENARIST_ID

    def is_composer(self):
        return self.id == COMPOSER_ID

    def is_musician(self):
        return self.id == MUSICIAN_ID
