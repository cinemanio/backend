from parameterized import parameterized
from graphql_jwt.shortcuts import get_token

from cinemanio.api.tests.base import AuthQueryBaseTestCase


class AuthTestCase(AuthQueryBaseTestCase):
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

    def test_get_token_for_active_user(self):
        user = self.create_user(is_active=True)
        with self.assertNumQueries(1):
            result = self.execute(self.token_auth_mutation, dict(username=user.username, password=self.password))
        self.assert_token(result['tokenAuth']['token'], user)

    def test_get_token_for_inactive_user(self):
        user = self.create_user(is_active=False)
        result = self.execute_with_errors(self.token_auth_mutation, dict(username=user.username,
                                                                         password=self.password))
        self.assert_empty_response_with_error(result, 'tokenAuth', 'Please, enter valid credentials')

    @parameterized.expand(['password', 'username'])
    def test_get_token_wrong_field(self, field_name):
        user = self.create_user(is_active=True)
        variables = dict(username=user.username, password=self.password)
        variables[field_name] = ''
        result = self.execute_with_errors(self.token_auth_mutation, variables)
        self.assert_empty_response_with_error(result, 'tokenAuth', 'Please, enter valid credentials')

    def test_verify_token(self):
        user = self.create_user()
        token = get_token(user)
        with self.assertNumQueries(0):
            result = self.execute(self.verify_token_mutation, dict(token=token))
        self.assert_payload(result['verifyToken']['payload'], user)

    @parameterized.expand(['', 'bad_token'])
    def test_verify_bad_token(self, token):
        result = self.execute_with_errors(self.verify_token_mutation, dict(token=token))
        self.assert_empty_response_with_error(result, 'verifyToken', 'Error decoding signature')

    def test_refresh_token(self):
        user = self.create_user()
        token = get_token(user)
        with self.assertNumQueries(1):
            result = self.execute(self.refresh_token_mutation, dict(token=token))
        self.assert_token(result['refreshToken']['token'], user)
        self.assert_payload(result['refreshToken']['payload'], user)

    @parameterized.expand(['', 'bad_token'])
    def test_refresh_bad_token(self, token):
        result = self.execute_with_errors(self.refresh_token_mutation, dict(token=token))
        self.assert_empty_response_with_error(result, 'refreshToken', 'Error decoding signature')
