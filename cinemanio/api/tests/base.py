from recordclass import recordclass
from graphql_jwt.shortcuts import get_token

from cinemanio.core.tests.base import BaseTestCase
from cinemanio.users.factories import UserFactory
from cinemanio.schema import schema


class QueryBaseTestCase(BaseTestCase):
    user = None
    password = "secret"
    Context = recordclass("Request", ["user", "Meta", "META"])

    def get_context(self, user=None):
        if user is None:
            return self.Context(user=None, Meta={}, META={})
        token = get_token(user)
        headers = {"HTTP_AUTHORIZATION": f"JWT {token}"}
        return self.Context(user=user, Meta=headers, META=headers)

    def create_user(self, **kwargs):
        self.user = UserFactory(username="user", **kwargs)
        self.user.set_password(self.password)
        self.user.save()

    def _execute(self, query, values=None, context=None):
        return schema.execute(query, variable_values=values, context_value=context or self.get_context(self.user))

    def execute(self, query, values=None, context=None):
        result = self._execute(query, values, context)
        assert not result.errors, result.errors
        return result.data

    def execute_with_errors(self, query, values=None, context=None):
        result = self._execute(query, values, context)
        assert result.errors, result.data
        return result


class ListQueryBaseTestCase(QueryBaseTestCase):
    def assert_count_equal(self, result, count):
        self.assertGreater(count, 0)
        self.assertEqual(len(result["edges"]), count)

    def assert_response_order(self, query, query_name, order_by, queries_count, earliest, latest, get_value):
        self.assertNotEqual(earliest, latest)

        with self.assertNumQueries(queries_count):
            result = self.execute(query, dict(order=order_by))

        count = len(result[query_name]["edges"]) - 1
        self.assertEqual(get_value(result[query_name]["edges"][0]["node"]), earliest)
        self.assertEqual(get_value(result[query_name]["edges"][count]["node"]), latest)

        with self.assertNumQueries(queries_count):
            result = self.execute(query, dict(order="-" + order_by))

        count = len(result[query_name]["edges"]) - 1
        self.assertEqual(get_value(result[query_name]["edges"][0]["node"]), latest)
        self.assertEqual(get_value(result[query_name]["edges"][count]["node"]), earliest)


class ObjectQueryBaseTestCase(QueryBaseTestCase):
    def assert_m2m_rel(self, result, queryset, fieldname="nameEn"):
        self.assertListEqual([r[fieldname] for r in result], list(queryset.values_list("name_en", flat=True)))
