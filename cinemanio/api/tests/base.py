from recordclass import recordclass
from graphql_jwt.shortcuts import get_token

from cinemanio.core.tests.base import BaseTestCase
from cinemanio.users.factories import UserFactory
from cinemanio.schema import schema


class QueryBaseTestCase(BaseTestCase):
    user = None
    password = 'secret'
    Context = recordclass('Request', ['user', 'Meta', 'META'])

    def get_context(self, user=None):
        if user is None:
            return self.Context(user=None, Meta={}, META={})
        token = get_token(user)
        headers = {'HTTP_AUTHORIZATION': f'JWT {token}'}
        return self.Context(user=user, Meta=headers, META=headers)

    def create_user(self, **kwargs):
        self.user = UserFactory(username='user', **kwargs)
        self.user.set_password(self.password)
        self.user.save()

    def _execute(self, query, values=None, context=None):
        return schema.execute(query, variable_values=values, context_value=context or self.get_context(self.user))

    def execute(self, query, values=None, context=None):
        result = self._execute(query, values, context)
        self.assertIsNone(result.errors, result.errors)
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
