import graphene
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import SetPasswordForm, PasswordChangeForm
from django.contrib.auth.tokens import default_token_generator as token_generator
from django.core.exceptions import ValidationError, ImproperlyConfigured
from django.core.validators import validate_email
from django.utils.encoding import force_text, force_bytes
from django.utils.http import urlsafe_base64_encode as uid_encoder, urlsafe_base64_decode as uid_decoder
from graphene import relay, AbstractType
from graphene.types.generic import GenericScalar
from graphene_django import DjangoObjectType
from graphql_extensions.auth.decorators import login_required
from graphql_jwt.shortcuts import get_token, get_payload
from django_registration.backends.activation.views import RegistrationView, ActivationView, ActivationError

from cinemanio.users.emails.signals import (
    user_registered, user_activated, change_password_confirmation, reset_password_requested,
)

User = get_user_model()

ACTIVATE_USER_URL_TEMPLATE = settings.ACTIVATE_USER_URL_TEMPLATE
PASSWORD_RESET_URL_TEMPLATE = settings.PASSWORD_RESET_URL_TEMPLATE
ACCOUNT_ACTIVATION_DAYS = settings.ACCOUNT_ACTIVATION_DAYS

settings_check_map = {
    'ACTIVATE_USER_URL_TEMPLATE': ['key'],
    'PASSWORD_RESET_URL_TEMPLATE': ['uid', 'token'],
}
for const, vars in settings_check_map.items():
    for var in vars:
        if f'%({var})s' not in globals()[const]:
            raise ImproperlyConfigured(f'{const} must contain var %({var})s')


class DynamicUsernameMeta(type):
    def __new__(mcs, classname, bases, dictionary):
        dictionary[User.USERNAME_FIELD] = graphene.String(required=True)
        return type.__new__(mcs, classname, bases, dictionary)


class UpdateUsernameMeta(type):
    def __new__(mcs, classname, bases, dictionary):
        for field in ('email', 'username', 'first_name', 'last_name',):
            dictionary[field] = graphene.String()
        return type.__new__(mcs, classname, bases, dictionary)


class UserNode(DjangoObjectType):
    class Meta:
        model = User
        interfaces = (relay.Node,)
        only_fields = ('email', 'username', 'first_name', 'last_name',)
        filter_fields = ('email', 'username', 'first_name', 'last_name',)

    @classmethod
    def get_node(cls, info, id):
        user = super(UserNode, cls).get_node(info, id)
        if info.context.user.id and (user.id == info.context.user.id or info.context.user.is_staff):
            return user
        else:
            return None


class RegisterUser(graphene.Mutation):
    class Arguments(metaclass=DynamicUsernameMeta):
        email = graphene.String(required=True)
        password = graphene.String()
        first_name = graphene.String()
        last_name = graphene.String()

    ok = graphene.Boolean()

    @classmethod
    def mutate(cls, root, info, **kwargs):
        email = kwargs.pop('email')
        username = kwargs.pop(User.USERNAME_FIELD, email)
        password = kwargs.pop('password') if 'password' in kwargs else User.objects.make_random_password()

        try:
            validate_email(email)
        except ValidationError as e:
            raise ValueError(e.message)

        user = User.objects.create_user(username, email, password, is_active=False, **kwargs)
        key = RegistrationView().get_activation_key(user)
        link = ACTIVATE_USER_URL_TEMPLATE.format(key=key)

        user_registered.send(sender=User, user=user, password=password, link=link,
                             expiration_days=ACCOUNT_ACTIVATION_DAYS, request=info.context)

        return cls(ok=True)


class ActivateUser(graphene.Mutation):
    class Arguments:
        key = graphene.String(required=True)

    user = graphene.Field(UserNode)
    token = graphene.String()
    payload = GenericScalar()

    @classmethod
    def mutate(cls, root, info, **kwargs):
        key = kwargs.pop('key')

        try:
            user = ActivationView().activate(activation_key=key)
        except ActivationError as e:
            raise ValueError(e.message)

        token = get_token(user, info.context)
        payload = get_payload(token, info.context)

        user_activated.send(sender=User, user=user, request=info.context)

        return cls(user=user, token=token, payload=payload)


class ResetPasswordRequest(graphene.Mutation):
    class Arguments:
        email = graphene.String(required=True)

    ok = graphene.Boolean()

    @classmethod
    def mutate(cls, root, info, **kwargs):
        email = kwargs.pop('email')

        try:
            validate_email(email)
        except ValidationError as e:
            raise ValueError(e.message)

        for user in User.objects.filter(email=email):
            uid = uid_encoder(force_bytes(user.pk)).decode()
            token = token_generator.make_token(user)
            link = PASSWORD_RESET_URL_TEMPLATE.format(token=token, uid=uid)
            reset_password_requested.send(sender=User, user=user, link=link, request=info.context)

        return cls(ok=True)


class ResetPassword(graphene.Mutation):
    class Arguments:
        password = graphene.String(required=True)
        uid = graphene.String(required=True)
        token = graphene.String(required=True)

    user = graphene.Field(UserNode)

    @classmethod
    def mutate(cls, root, info, **kwargs):
        data = {
            'uid': kwargs.get('uid'),
            'token': kwargs.get('token'),
            'new_password1': kwargs.get('password'),
            'new_password2': kwargs.get('password')
        }

        try:
            uid = force_text(uid_decoder(data['uid']))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            raise ValueError('The uid is not valid.')

        form = SetPasswordForm(user=user, data=data)

        if not form.is_valid() or not token_generator.check_token(user, data['token']):
            raise ValueError("The token is not valid.")

        form.save()
        change_password_confirmation.send(sender=User, user=user, request=info.context)

        return cls(user=user)


class ChangePassword(graphene.Mutation):
    class Arguments:
        old_password = graphene.String(required=True)
        new_password1 = graphene.String(required=True)
        new_password2 = graphene.String(required=True)

    user = graphene.Field(UserNode)

    @classmethod
    @login_required
    def mutate(cls, root, info, **kwargs):
        data = {
            'old_password': kwargs.get('old_password'),
            'new_password1': kwargs.get('new_password1'),
            'new_password2': kwargs.get('new_password2')
        }
        user = info.context.user
        form = PasswordChangeForm(user=user, data=data)

        if not form.is_valid():
            for error in form.errors.values():
                raise ValueError(error[0])

        form.save()
        change_password_confirmation.send(sender=User, user=user, request=info.context)

        return cls(user=user)


class UpdateUser(graphene.Mutation):
    class Arguments(metaclass=UpdateUsernameMeta):
        pass

    user = graphene.Field(UserNode)

    @classmethod
    @login_required
    def mutate(cls, root, info, **kwargs):
        user = info.context.user

        for key, value in kwargs.items():
            setattr(user, key, value)

        user.save()
        return cls(user=user)


class RegistrationMutation(AbstractType):
    register_user = RegisterUser.Field()
    activate_user = ActivateUser.Field()
    reset_password_request = ResetPasswordRequest.Field()
    reset_password = ResetPassword.Field()
    change_password = ChangePassword.Field()
    update_user = UpdateUser.Field()
