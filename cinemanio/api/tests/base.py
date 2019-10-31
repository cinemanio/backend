import time
from typing import Dict

from graphql_jwt.shortcuts import get_token, get_user_by_token
from django.contrib.auth.models import AnonymousUser

from cinemanio.api.helpers import global_id
from cinemanio.core.tests.base import BaseTestCase
from cinemanio.users.models import User
from cinemanio.users.factories import UserFactory
from cinemanio.schema import schema


class Context:
    _jwt_token_auth = None
    user = AnonymousUser()
    Meta: Dict[str, str] = {}
    META: Dict[str, str] = {}

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    def is_secure(self):
        return True

    def get_host(self):
        return ''


class QueryBaseTestCase(BaseTestCase):
    user = None
    password = 'secret'

    def get_context(self, user=None):
        kwargs = {}
        if user:
            token = get_token(user)
            headers = {'HTTP_AUTHORIZATION': f'JWT {token}'}
            kwargs['user'] = user
            kwargs['Meta'] = kwargs['META'] = headers
        return Context(**kwargs)

    def get_user(self, **kwargs):
        user = UserFactory.build(username='user', **kwargs)
        user.set_password(self.password)
        return user

    def create_user(self, **kwargs):
        user = self.get_user(**kwargs)
        user.save()
        return user

    def _execute(self, query, values=None, context=None):
        return schema.execute(query, variable_values=values, context_value=context or self.get_context(self.user))

    def execute(self, query, values=None, context=None):
        result = self._execute(query, values, context)
        self.assertIsNone(result.errors, result.to_dict())
        return result.data

    def execute_with_errors(self, query, values=None, context=None):
        result = self._execute(query, values, context)
        self.assertIsNotNone(result.errors, result.data)
        return result


class ListQueryBaseTestCase(QueryBaseTestCase):
    count = 100

    def assert_count_equal(self, result, count):
        """
        Check there are items in API response and amount is equal to count argument
        :param result: API response
        :param count: expected amount of items in API response
        """
        self.assertGreater(count, 0)
        self.assertEqual(len(result['edges']), count)

    def assert_response_orders(self, *args, **kwargs):
        """
        Check result is ordered the same way as queryset
        Execute query 2 times with order_by parameter ASC and DESC
        """
        self.assert_response_order(*args, **kwargs)
        kwargs['order_by'] = '-' + kwargs['order_by']
        self.assert_response_order(*args, **kwargs)

    def assert_response_order(self, query, query_name, order_by, queries_count, model,
                              get_value_instance, get_value_result):
        """
        Check first and last items of result contains different values
        Check result is ordered the same way as queryset
        :param query: search query
        :param query_name: root of search query
        :param order_by: sort param
        :param queries_count: number of DB queries
        :param model: model
        :param get_value_result: get value method of result
        :param get_value_instance: get value method of instance
        """
        with self.assertNumQueries(queries_count):
            result = self.execute(query, dict(order=order_by))

        self.assertEqual(len(result[query_name]['edges']), self.count)
        self.assertNotEqual(get_value_result(result[query_name]['edges'][0]['node']),
                            get_value_result(result[query_name]['edges'][self.count - 1]['node']))
        for i, instance in enumerate(model.objects.order_by(order_by)):
            self.assertEqual(get_value_result(result[query_name]['edges'][i]['node']), get_value_instance(instance))


class ObjectQueryBaseTestCase(QueryBaseTestCase):
    def assert_m2m_rel(self, result, queryset, fieldname='nameEn'):
        self.assertListEqual([r[fieldname] for r in result], list(queryset.values_list('name_en', flat=True)))


class AuthQueryBaseTestCase(QueryBaseTestCase):
    def assert_payload(self, payload, user):
        self.assertEqual(payload['username'], user.username)
        self.assertGreater(payload['exp'] - time.time(), 300 - 2)
        self.assertLess(payload['origIat'] - time.time(), 0)

    def assert_token(self, token, user):
        user = User.objects.get(username=user.username)
        self.assertEqual(len(token), 157)
        self.assertEqual(get_user_by_token(token), user)

    def assert_empty_response_with_error(self, result, key, error):
        self.assertTrue(result.data, msg=result.to_dict())
        self.assertEqual(result.data[key], None)
        self.assertEqual(str(result.errors[0].original_error), error)

    def assert_user(self, result, user):
        user = User.objects.get(username=user.username)
        self.assertDictEqual(result, dict(
            id=global_id(user), username=user.username, email=user.email,
            firstName=user.first_name, lastName=user.last_name))
