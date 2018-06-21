import time

from graphql_jwt.shortcuts import get_token

from cinemanio.api.tests.base import QueryBaseTestCase


class AuthTestCase(QueryBaseTestCase):
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

    def assert_payload(self, payload):
        self.assertEqual(payload['username'], self.user.username)
        self.assertGreater(payload['exp'] - time.time(), 300 - 2)
        self.assertLess(payload['orig_iat'] - time.time(), 0)

    def test_get_token_for_active_user(self):
        self.create_user(is_active=True)
        with self.assertNumQueries(1):
            result = self.execute(self.token_auth_mutation, dict(username=self.user.username, password=self.password))
        self.assertTrue(len(result['tokenAuth']['token']), 159)

    def test_get_token_for_inactive_user(self):
        self.create_user(is_active=False)
        with self.assertRaises(AssertionError):
            self.execute(self.token_auth_mutation, dict(username=self.user.username, password=self.password))

    def test_verify_token(self):
        self.create_user()
        token = get_token(self.user)
        with self.assertNumQueries(0):
            result = self.execute(self.verify_token_mutation, dict(token=token))
        self.assert_payload(result['verifyToken']['payload'])

    def test_verify_bad_token(self):
        with self.assertRaises(AssertionError):
            self.execute(self.verify_token_mutation, dict(token='bad_token'))

    def refresh_token(self):
        self.create_user()
        token = get_token(self.user)
        with self.assertNumQueries(1):
            result = self.execute(self.refresh_token_mutation, dict(token=token))
        self.assertTrue(len(result['refreshToken']['token']), 159)
        self.assert_payload(result['refreshToken']['payload'])
