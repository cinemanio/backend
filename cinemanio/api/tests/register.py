from django.contrib.auth import authenticate
from django.contrib.auth.tokens import default_token_generator as token_generator
from django.core import mail
from django.test import override_settings
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django_registration.backends.activation.views import RegistrationView
from parameterized import parameterized

from cinemanio.api.tests.base import AuthQueryBaseTestCase
from cinemanio.users.models import User

user_fragment = '''
    user {
      id
      username
      email
      firstName
      lastName
    }
'''


class RegisterUserTestCase(AuthQueryBaseTestCase):
    register_user_mutation = '''
        mutation RegisterUser(
          $username: String!, $email: String!, $password: String!, $firstName: String, $lastName: String
        ) {
          registerUser(
            username: $username, email: $email, password: $password, firstName: $firstName, lastName: $lastName
          ) {
            ok
          }
        }
    '''

    def test_register_user(self):
        user = self.get_user()
        with self.assertNumQueries(1):
            result = self.execute(self.register_user_mutation,
                                  dict(username=user.username, password=self.password, email=user.email,
                                       firstName=user.first_name, lastName=user.last_name))
        self.assertTrue(result['registerUser']['ok'])
        self.assertFalse(User.objects.get(username=user.username).is_active)
        self.assertEqual(len(mail.outbox), 1)

    @parameterized.expand(['', 'wrong'])
    def test_register_user_invalid_email(self, email):
        user = self.get_user()
        variables = dict(username=user.username, password=self.password, email=email)
        result = self.execute_with_errors(self.register_user_mutation, variables)
        self.assert_empty_response_with_error(result, 'registerUser', 'Enter a valid email address.')


class ActivateUserTestCase(AuthQueryBaseTestCase):
    activate_user_mutation = '''
        mutation ActivateUser($key: String!) {
          activateUser(key: $key) {
            %(user)s
            token
            payload
          }
        }
    ''' % dict(user=user_fragment)

    def test_activate_user(self):
        user = self.create_user(is_active=False)
        key = RegistrationView().get_activation_key(user)
        with self.assertNumQueries(2):
            result = self.execute(self.activate_user_mutation, dict(key=key))
        self.assertTrue(authenticate(username=user.username, password=self.password))
        self.assert_token(result['activateUser']['token'], user)
        self.assert_payload(result['activateUser']['payload'], user)
        self.assert_user(result['activateUser']['user'], user)
        self.assertTrue(User.objects.get(username=user.username).is_active)
        self.assertEqual(len(mail.outbox), 1)

    @parameterized.expand(['', 'wrong'])
    def test_activate_user_invalid_key(self, key):
        self.create_user(is_active=False)
        result = self.execute_with_errors(self.activate_user_mutation, dict(key=key))
        self.assert_empty_response_with_error(result, 'activateUser', 'The activation key you provided is invalid.')

    def test_activate_user_token_of_another_user(self):
        self.create_user(is_active=False)
        key = RegistrationView().get_activation_key(User(username='username'))
        result = self.execute_with_errors(self.activate_user_mutation, dict(key=key))
        self.assert_empty_response_with_error(result, 'activateUser',
                                              'The account you attempted to activate is invalid.')

    def test_activate_user_already_activated(self):
        user = self.create_user(is_active=True)
        key = RegistrationView().get_activation_key(user)
        result = self.execute_with_errors(self.activate_user_mutation, dict(key=key))
        self.assert_empty_response_with_error(result, 'activateUser',
                                              'The account you tried to activate has already been activated.')

    @override_settings(ACCOUNT_ACTIVATION_DAYS=0)
    def test_activate_user_with_key_expired(self):
        user = self.create_user(is_active=False)
        key = RegistrationView().get_activation_key(user)
        result = self.execute_with_errors(self.activate_user_mutation, dict(key=key))
        self.assert_empty_response_with_error(result, 'activateUser', 'This account has expired.')


class ResetPasswordRequestTestCase(AuthQueryBaseTestCase):
    reset_password_request_mutation = '''
        mutation ResetPasswordRequest($email: String!) {
          resetPasswordRequest(email: $email) {
            ok
          }
        }
    '''

    def test_reset_password_request(self):
        user = self.create_user()
        with self.assertNumQueries(1):
            result = self.execute(self.reset_password_request_mutation, dict(email=user.email))
        self.assertTrue(result['resetPasswordRequest']['ok'])
        self.assertEqual(len(mail.outbox), 1)

    @parameterized.expand(['', 'wrong'])
    def test_reset_password_request_invalid_email(self, email):
        self.create_user()
        result = self.execute_with_errors(self.reset_password_request_mutation, dict(email=email))
        self.assert_empty_response_with_error(result, 'resetPasswordRequest', 'Enter a valid email address.')


class ResetPasswordTestCase(AuthQueryBaseTestCase):
    reset_password_mutation = '''
        mutation ResetPassword($password: String!, $uid: String!, $token: String!) {
          resetPassword(password: $password, uid: $uid, token: $token) {
            %(user)s
            token
            payload
          }
        }
    ''' % dict(user=user_fragment)

    def test_reset_password(self):
        user = self.create_user()
        uid = urlsafe_base64_encode(force_bytes(user.pk)).decode()
        token = token_generator.make_token(user)
        with self.assertNumQueries(2):
            result = self.execute(self.reset_password_mutation, dict(password='new_password', uid=uid, token=token))
        self.assertTrue(authenticate(username=user.username, password='new_password'))
        self.assert_token(result['resetPassword']['token'], user)
        self.assert_payload(result['resetPassword']['payload'], user)
        self.assert_user(result['resetPassword']['user'], user)
        self.assertEqual(len(mail.outbox), 1)

    @parameterized.expand(['', 'wrong'])
    def test_reset_password_invalid_uid(self, uid):
        user = self.create_user()
        token = token_generator.make_token(user)
        result = self.execute_with_errors(self.reset_password_mutation, dict(password='new_password', uid=uid,
                                                                             token=token))
        self.assert_empty_response_with_error(result, 'resetPassword', 'The uid is not valid.')

    @parameterized.expand(['', 'wrong'])
    def test_reset_password_invalid_token(self, token):
        user = self.create_user()
        uid = urlsafe_base64_encode(force_bytes(user.pk)).decode()
        result = self.execute_with_errors(self.reset_password_mutation, dict(password='new_password', uid=uid,
                                                                             token=token))
        self.assert_empty_response_with_error(result, 'resetPassword', 'The token is not valid.')


class ChangePasswordTestCase(AuthQueryBaseTestCase):
    change_password_mutation = '''
        mutation ChangePassword($oldPassword: String!, $newPassword: String!) {
          changePassword(oldPassword: $oldPassword, newPassword: $newPassword) {
            ok
          }
        }
    '''

    def test_change_password(self):
        self.user = self.create_user()
        with self.assertNumQueries(1):
            result = self.execute(self.change_password_mutation, dict(oldPassword=self.password,
                                                                      newPassword='new_password'))
        self.assertTrue(authenticate(username=self.user.username, password='new_password'))
        self.assertTrue(result['changePassword']['ok'])
        self.assertEqual(len(mail.outbox), 1)

    @parameterized.expand([
        ('', 'new_password', 'This field is required.'),
        ('wrong', 'new_password', 'Your old password was entered incorrectly. Please enter it again.'),
        (None, '', 'This field is required.'),
        (None, 'short', 'This password is too short. It must contain at least 8 characters.'),
    ])
    def test_change_password_invalid_input(self, old_password, new_password, message):
        self.user = self.create_user()
        if old_password is None:
            old_password = self.password
        result = self.execute_with_errors(self.change_password_mutation, dict(oldPassword=old_password,
                                                                              newPassword=new_password))
        self.assert_empty_response_with_error(result, 'changePassword', message)

    def test_change_password_unauth_user(self):
        self.create_user()
        result = self.execute_with_errors(self.change_password_mutation, dict(oldPassword=self.password,
                                                                              newPassword='new_password'))
        self.assert_empty_response_with_error(result, 'changePassword',
                                              'You do not have permission to perform this action')


class UpdateUserTestCase(AuthQueryBaseTestCase):
    update_user_mutation = '''
        mutation UpdateUser($username: String!, $email: String!, $firstName: String, $lastName: String) {
          updateUser(username: $username, email: $email, firstName: $firstName, lastName: $lastName) {
            %(user)s
          }
        }
    ''' % dict(user=user_fragment)

    def test_update_user(self):
        self.user = self.create_user()
        user = self.user
        user.__dict__.update(dict(username='user1', email='user1@gmail.com',
                                  firstName='FirstName', lastName='LastName'))
        with self.assertNumQueries(1):
            result = self.execute(self.update_user_mutation,
                                  dict(username=user.username, email=user.email,
                                       firstName=user.first_name, lastName=user.last_name))
        self.assert_user(result['updateUser']['user'], user)

    def test_update_user_unauth_user(self):
        user = self.create_user()
        result = self.execute_with_errors(self.update_user_mutation,
                                          dict(username=user.username, email=user.email,
                                               firstName=user.first_name, lastName=user.last_name))
        self.assert_empty_response_with_error(result, 'updateUser',
                                              'You do not have permission to perform this action')
