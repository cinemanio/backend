from collections import namedtuple

from cinemanio.core.tests.base import BaseTestCase
from cinemanio.users.factories import UserFactory
from cinemanio.schema import schema


class QueryBaseTestCase(BaseTestCase):
    user = None
    password = 'secret'
    Context = namedtuple('Context', ['user'])

    @property
    def context(self):
        return self.Context(user=self.user)

    def create_user(self, **kwargs):
        self.user = UserFactory(username='user', **kwargs)
        self.user.set_password(self.password)
        self.user.save()

    def execute(self, query, values=None, context=None):
        result = schema.execute(query, variable_values=values, context_value=context or self.context)
        assert not result.errors, result.errors
        return result.data


class ListQueryBaseTestCase(QueryBaseTestCase):
    def assert_count_equal(self, result, count):
        self.assertGreater(count, 0)
        self.assertEqual(len(result['edges']), count)

    def assertResponseOrder(self, query, query_name, order_by, queries_count, earliest, latest, get_value):
        self.assertNotEqual(earliest, latest)

        with self.assertNumQueries(queries_count):
            result = self.execute(query, dict(order=order_by))

        count = len(result[query_name]['edges']) - 1
        self.assertEqual(get_value(result[query_name]['edges'][0]['node']), earliest)
        self.assertEqual(get_value(result[query_name]['edges'][count]['node']), latest)

        with self.assertNumQueries(queries_count):
            result = self.execute(query, dict(order='-' + order_by))

        count = len(result[query_name]['edges']) - 1
        self.assertEqual(get_value(result[query_name]['edges'][0]['node']), latest)
        self.assertEqual(get_value(result[query_name]['edges'][count]['node']), earliest)


class ObjectQueryBaseTestCase(QueryBaseTestCase):
    def assert_m2m_rel(self, result, queryset, fieldname='name'):
        self.assertListEqual([r[fieldname] for r in result], list(queryset.values_list('name', flat=True)))
