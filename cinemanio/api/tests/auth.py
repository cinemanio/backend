import time
from graphql_jwt.shortcuts import get_token

from cinemanio.api.tests.base import ObjectQueryBaseTestCase
from cinemanio.api.tests.helpers import execute
from cinemanio.users.factories import UserFactory


class AuthTestCase(ObjectQueryBaseTestCase):
    password = 'secret'
    token_auth_mutation = '''
        mutation TokenAuth($username: String!, $password: String!) {
          tokenAuth(username: $username, password: $password) {
            token
          }
        }
    '''
    verify_token_mutation = '''
        mutation VerifyToken($token: String!) {
          verifyToken(token: $token) {
            payload
          }
        }
    '''
    refresh_token_mutation = '''
        mutation RefreshToken($token: String!) {
          refreshToken(token: $token) {
            token
            payload
          }
        }
    '''

    def _create_user(self, **kwargs):
        user = UserFactory(username='user', **kwargs)
        user.set_password(self.password)
        user.save()
        return user

    def assertPayload(self, user, payload):
        self.assertEqual(payload['username'], user.username)
        self.assertGreater(payload['exp'] - time.time(), 230)
        self.assertLess(payload['orig_iat'] - time.time(), 0)

    def test_get_token_for_active_user(self):
        user = self._create_user(is_active=True)
        with self.assertNumQueries(1):
            result = execute(self.token_auth_mutation, dict(username=user.username, password=self.password))
        self.assertTrue(len(result['tokenAuth']['token']), 159)

    def test_get_token_for_inactive_user(self):
        user = self._create_user(is_active=False)
        with self.assertRaises(AssertionError):
            execute(self.token_auth_mutation, dict(username=user.username, password=self.password))

    def test_verify_token(self):
        user = self._create_user()
        token = get_token(user)
        with self.assertNumQueries(0):
            result = execute(self.verify_token_mutation, dict(token=token))
        self.assertPayload(user, result['verifyToken']['payload'])

    def test_verify_bad_token(self):
        with self.assertRaises(AssertionError):
            execute(self.verify_token_mutation, dict(token='bad_token'))

    def refresh_token(self):
        user = self._create_user()
        token = get_token(user)
        with self.assertNumQueries(1):
            result = execute(self.refresh_token_mutation, dict(token=token))
        self.assertTrue(len(result['refreshToken']['token']), 159)
        self.assertPayload(user, result['refreshToken']['payload'])
