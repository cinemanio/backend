from parameterized import parameterized

from cinemanio.api.tests.base import ListQueryBaseTestCase
from cinemanio.core.factories import MovieFactory, PersonFactory


class PaginationQueryTestCase(ListQueryBaseTestCase):
    def populated_cursors(self, cursors, result):
        for cursor in result['edges']:
            cursors.add(cursor['cursor'])

    @parameterized.expand([
        (MovieFactory,),
        (PersonFactory,),
    ])
    def test_object_pagination(self, factory):
        for i in range(100):
            instance = factory()
        query_name = instance._meta.model_name + 's'
        query = '''
            query Objects($after: String!){
              %s(first: 10, after: $after) {
                totalCount
                edges {
                  node {
                    id
                  }
                  cursor
                }
                pageInfo {
                  endCursor
                  hasNextPage
                }
              }
            }
        ''' % query_name
        # TODO: remove one extra SELECT COUNT(*) AS "__count" FROM "core_movie"
        with self.assertNumQueries(3):
            result = self.execute(query, dict(after=''))
        self.assert_count_equal(result[query_name], 10)
        self.assertEqual(result[query_name]['totalCount'], 100)

        cursors = set()
        self.populated_cursors(cursors, result[query_name])

        for i in range(10):
            values = dict(after=result[query_name]['pageInfo']['endCursor'])
            if i == 9:
                with self.assertNumQueries(2):
                    result = self.execute(query, values)
                self.assertEqual(len(result[query_name]['edges']), 0)
            else:
                with self.assertNumQueries(3):
                    result = self.execute(query, values)
                self.assert_count_equal(result[query_name], 10)
                self.populated_cursors(cursors, result[query_name])

        self.assertEqual(len(cursors), 100)
