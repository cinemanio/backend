from django.dispatch import Signal, receiver

from cinemanio.users.models import User
from .utils import send_email

user_registered = Signal(providing_args=['user', 'password', 'link', 'expiration_days', 'request'])
user_activated = Signal(providing_args=['user', 'request'])
reset_password_requested = Signal(providing_args=['user', 'link', 'request'])
change_password_confirmation = Signal(providing_args=['user', 'request'])


@receiver(user_registered, sender=User)
def send_welcome_email_signal(sender, user, password, link, expiration_days, request, **_):
    send_email(user=user, request=request,
               template_name='welcome', context={'link': link, 'expiration_days': expiration_days, 'password': password})


@receiver(user_activated, sender=User)
def send_activation_email_signal(sender, user, request, **_):
    send_email(user=user, request=request,
               template_name='activation')


@receiver(reset_password_requested, sender=User)
def send_reset_password_link_email_signal(sender, user, link, request, **_):
    send_email(user=user, request=request,
               template_name='reset_password_link', context={'link': link})


@receiver(change_password_confirmation, sender=User)
def send_change_password_confirmation_email_signal(sender, user, request, **_):
    send_email(user=user, request=request,
               template_name='change_password_confirmation')
