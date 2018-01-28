from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import ugettext_lazy as _

from cinemanio.attitudes.models.base import AttitudeBase, register_attitude_fields
from cinemanio.core.models import Person


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
    object = models.OneToOneField(Person, related_name='attitudes_count', on_delete=models.CASCADE)


get_user_model().add_to_class('familiar_persons', models.ManyToManyField(
    Person, verbose_name=_('Attitudes'), through=PersonAttitude, related_name='attitudes_users'))

register_attitude_fields(PersonAttitude, PersonAttitudeCount)
