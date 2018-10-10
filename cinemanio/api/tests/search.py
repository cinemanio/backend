from unittest import mock
from parameterized import parameterized

from cinemanio.api.helpers import global_id
from cinemanio.api.tests.base import ListQueryBaseTestCase
from cinemanio.core.factories import MovieFactory, PersonFactory


class SearchQueryTestCase(ListQueryBaseTestCase):
    search_query = '''
        query Objects($search: String!, $order: String!){
          %s(search: $search, orderBy: $order) {
            edges {
              node {
                id
              }
            }
          }
        }
    '''

    def prepare_stuff(self, factory, raw_search):
        instances = []
        for i in range(100):
            instances.append(factory())

        raw_search.return_value = {'hits': [
            {'objectID': instances[0].id},
            {'objectID': instances[1].id},
            {'objectID': instances[2].id},
        ]}

        query_name = instances[0]._meta.model_name + 's'
        return instances, query_name

    @parameterized.expand([
        (MovieFactory,),
        (PersonFactory,),
    ])
    @mock.patch('cinemanio.core.models.base.raw_search')
    def test_search_query(self, factory, raw_search):
        instances, query_name = self.prepare_stuff(factory, raw_search)

        with self.assertNumQueries(2):
            result = self.execute(self.search_query % query_name, dict(search='term', order=''))

        self.assert_count_equal(result[query_name], 3)
        self.assertEqual(result[query_name]['edges'][0]['node']['id'], global_id(instances[0]))
        self.assertEqual(result[query_name]['edges'][1]['node']['id'], global_id(instances[1]))
        self.assertEqual(result[query_name]['edges'][2]['node']['id'], global_id(instances[2]))

    @mock.patch('cinemanio.core.models.base.raw_search')
    def test_search_query_with_order_specified(self, raw_search):
        instances, query_name = self.prepare_stuff(MovieFactory, raw_search)

        instances[0].year = 2002
        instances[0].save()
        instances[1].year = 2003
        instances[1].save()
        instances[2].year = 2001
        instances[2].save()

        with self.assertNumQueries(2):
            result = self.execute(self.search_query % query_name, dict(search='term', order='year'))

        self.assert_count_equal(result[query_name], 3)
        self.assertEqual(result[query_name]['edges'][0]['node']['id'], global_id(instances[2]))
        self.assertEqual(result[query_name]['edges'][1]['node']['id'], global_id(instances[0]))
        self.assertEqual(result[query_name]['edges'][2]['node']['id'], global_id(instances[1]))
