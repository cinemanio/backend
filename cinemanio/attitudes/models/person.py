from django.db import models
from django.utils.translation import ugettext_lazy as _

from cinemanio.core.models import Person
from cinemanio.attitudes.models.base import AttitudeBase, register_attitude_fields


class PersonAttitude(AttitudeBase):
    class Meta(AttitudeBase.Meta):
        pass

    object = models.ForeignKey(Person, related_name='attitudes', on_delete=models.CASCADE)
    fields = (
        ('fav', _('Fav'), _('Faved'), _('faved person'), _('You faved person %s')),
        ('like', _('Like'), _('Liked'), _('liked person'), _('You liked person %s')),
        ('dislike', _('Dislike'), _('Disliked'), _('disliked person'), _('You disliked person %s')),
    )

    def correct_fields(self, name, value):
        if value is True:
            if name == 'like':
                self.dislike = False
            if name == 'dislike':
                self.like = False
                self.fav = False
            if name == 'fav':
                self.like = True
                self.dislike = False

        if value is False:
            if name == 'like':
                self.fav = False


class PersonAttitudeCount(models.Model):
    object = models.ForeignKey(Person, related_name='attitudes_count', on_delete=models.CASCADE)


register_attitude_fields(PersonAttitude, PersonAttitudeCount)
