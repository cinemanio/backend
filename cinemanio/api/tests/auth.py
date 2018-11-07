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
        self.assertLess(payload['origIat'] - time.time(), 0)

    def assert_empty_response_with_error(self, result, key, error):
        self.assertEqual(result.data[key], None)
        self.assertEqual(str(result.errors[0].original_error), error)

    def test_get_token_for_active_user(self):
        self.create_user(is_active=True)
        with self.assertNumQueries(1):
            result = self.execute(self.token_auth_mutation, dict(username=self.user.username, password=self.password))
        self.assertTrue(len(result['tokenAuth']['token']), 159)
        self.assertEqual(result['tokenAuth']['token'], get_token(self.user))

    def test_get_token_for_inactive_user(self):
        self.create_user(is_active=False)
        result = self.execute_with_errors(self.token_auth_mutation, dict(username=self.user.username,
                                                                         password=self.password))
        self.assert_empty_response_with_error(result, 'tokenAuth', 'Please, enter valid credentials')

    def test_get_token_wrong_username(self):
        self.create_user(is_active=True)
        result = self.execute_with_errors(self.token_auth_mutation, dict(username=self.user.username, password=''))
        self.assert_empty_response_with_error(result, 'tokenAuth', 'Please, enter valid credentials')

    def test_get_token_wrong_password(self):
        self.create_user(is_active=True)
        result = self.execute_with_errors(self.token_auth_mutation, dict(username='', password=self.password))
        self.assert_empty_response_with_error(result, 'tokenAuth', 'Please, enter valid credentials')

    def test_verify_token(self):
        self.create_user()
        token = get_token(self.user)
        with self.assertNumQueries(0):
            result = self.execute(self.verify_token_mutation, dict(token=token))
        self.assert_payload(result['verifyToken']['payload'])

    def test_verify_bad_token(self):
        result = self.execute_with_errors(self.verify_token_mutation, dict(token='bad_token'))
        self.assert_empty_response_with_error(result, 'verifyToken', 'Error decoding signature')

    def test_refresh_token(self):
        self.create_user()
        token = get_token(self.user)
        with self.assertNumQueries(1):
            result = self.execute(self.refresh_token_mutation, dict(token=token))
        self.assertTrue(len(result['refreshToken']['token']), 159)
        self.assertEqual(result['refreshToken']['token'], get_token(self.user))
        self.assert_payload(result['refreshToken']['payload'])

    def test_refresh_bad_token(self):
        result = self.execute_with_errors(self.refresh_token_mutation, dict(token='bad_token'))
        self.assert_empty_response_with_error(result, 'refreshToken', 'Error decoding signature')
