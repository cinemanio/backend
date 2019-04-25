from cinemanio.api.helpers import global_id
from cinemanio.api.tests.base import AuthQueryBaseTestCase


class UserQueryTestCase(AuthQueryBaseTestCase):
    me_query = '''
        query Me {
          me {
            id
            username
            email
            firstName
            lastName
          }
        }
    '''

    def test_me(self):
        self.user = self.create_user()
        with self.assertNumQueries(1):
            result = self.execute(self.me_query)
        self.assertEqual(result['me']['id'], global_id(self.user))
        self.assertEqual(result['me']['username'], self.user.username)
        self.assertEqual(result['me']['email'], self.user.email)
        self.assertEqual(result['me']['firstName'], self.user.first_name)
        self.assertEqual(result['me']['lastName'], self.user.last_name)

    def test_me_unathenticated(self):
        self.create_user()
        result = self.execute_with_errors(self.me_query)
        self.assert_empty_response_with_error(result, 'me', 'You do not have permission to perform this action')
