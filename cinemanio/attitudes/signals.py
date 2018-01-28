from django.dispatch import Signal
from django.dispatch import receiver

from cinemanio.attitudes.models import MovieAttitude, PersonAttitude, UserAttitude
from cinemanio.attitudes.tasks import DeleteEmptyAttitudes

attitude_changed = Signal(providing_args=['instance', 'code', 'request'])


@receiver(attitude_changed, sender=MovieAttitude)
@receiver(attitude_changed, sender=PersonAttitude)
@receiver(attitude_changed, sender=UserAttitude)
def delete_empty_attitudes(sender, instance, **kwargs):
    """
    Delete record if all attitudes are False
    """
    DeleteEmptyAttitudes.delay(sender, instance.id)
