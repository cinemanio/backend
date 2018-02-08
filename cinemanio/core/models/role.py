from django.db import models
from django.utils.translation import ugettext_lazy as _

from cinemanio.core.models.properties import PropertyModel


class RoleManager(models.Manager):
    def get_actor(self):
        return self.get(id=Role.ACTOR_ID)

    def get_director(self):
        return self.get(id=Role.DIRECTOR_ID)

    def get_author(self):
        return self.get(id=Role.AUTHOR_ID)

    def get_operator(self):
        return self.get(id=Role.OPERATOR_ID)

    def get_scenarist(self):
        return self.get(id=Role.SCENARIST_ID)

    def get_composer(self):
        return self.get(id=Role.COMPOSER_ID)

    def get_producer(self):
        return self.get(id=Role.PRODUCER_ID)


class Role(PropertyModel):
    """
    Role model
    """
    ACTOR_ID = 1
    ACTOR_VOICE_ID = 22
    DIRECTOR_ID = 16
    SCENARIST_ID = 18
    OPERATOR_ID = 10
    PRODUCER_ID = 14
    COMPOSER_ID = 7
    EDITOR_ID = 15
    AUTHOR_ID = 12
    MUSICIAN_ID = 21
    WRITER_ID = 12

    objects = RoleManager()

    class Meta(PropertyModel.Meta):
        verbose_name = _('role')
        verbose_name_plural = _('roles')

    def get_name(self, gender=1):
        # TODO: conversion Actor -> Actress depends on gender
        return self.name

    def is_actor(self):
        return self.id == self.ACTOR_ID

    def is_director(self):
        return self.id == self.DIRECTOR_ID

    def is_author(self):
        return self.id == self.AUTHOR_ID

    def is_operator(self):
        return self.id == self.OPERATOR_ID

    def is_scenarist(self):
        return self.id == self.SCENARIST_ID

    def is_composer(self):
        return self.id == self.COMPOSER_ID

    def is_musician(self):
        return self.id == self.MUSICIAN_ID
