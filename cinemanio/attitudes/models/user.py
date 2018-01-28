from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import ugettext_lazy as _

from cinemanio.attitudes.models.base import AttitudeBase, register_attitude_fields

User = get_user_model()


class UserAttitude(AttitudeBase):
    class Meta(AttitudeBase.Meta):
        pass

    object = models.ForeignKey(User, related_name='attitudes', on_delete=models.CASCADE)
    fields = (
        ('friend', _('Friend'), _('Friends'), _('started friendship with user'),
         _('You started friendship with user %s')),
        ('expert', _('Expert'), _('Experts'), _('thought user is an expert'), _('You think user %s is an expert')),
    )

    # def is_backward_attitude(self):
    #     try:
    #         backward_attitude = ProfileAttitude.objects.get(user=self.object, object=self.user)
    #         assert backward_attitude.friend or backward_attitude.expert
    #         return True
    #     except (ProfileAttitude.DoesNotExist, AssertionError):
    #         return False


class UserAttitudeCount(models.Model):
    object = models.ForeignKey(User, related_name='attitudes_count', on_delete=models.CASCADE)


register_attitude_fields(UserAttitude, UserAttitudeCount)
