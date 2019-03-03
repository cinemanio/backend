from django.core import mail

from cinemanio.api.tests.base import QueryBaseTestCase
from cinemanio.users.emails.signals import (
    user_registered, user_activated, change_password_confirmation, reset_password_requested
)
from cinemanio.users.models import User


class EmailsTest(QueryBaseTestCase):

    def assert_email(self, user):
        self.assertEqual(len(mail.outbox), 1)
        email = mail.outbox[0]
        self.assertTrue(user.username in email.subject)
        self.assertTrue(user.get_full_name() in email.body)

    def test_welcome_email(self):
        user = self.create_user()
        user_registered.send(sender=User, user=user, password='password', link='link', expiration_days=7, request={})
        self.assert_email(user)
        self.assertTrue(user.email in mail.outbox[0].body)
        self.assertTrue('password' in mail.outbox[0].body)

    def test_activation_email(self):
        user = self.create_user()
        user_activated.send(sender=User, user=user, request={})
        self.assert_email(user)

    def test_reset_password_link_email(self):
        user = self.create_user()
        reset_password_requested.send(sender=User, user=user, link='link', request={})
        self.assert_email(user)

    def test_change_password_confirmation_email(self):
        user = self.create_user()
        change_password_confirmation.send(sender=User, user=user, request={})
        self.assert_email(user)
