from django.conf import settings
from templated_email import send_templated_mail


def send_email(user, request, **kwargs):
    if 'context' not in kwargs:
        kwargs['context'] = {}

    kwargs['context'].update({'user': user})

    return send_templated_mail(
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        **kwargs
    )
