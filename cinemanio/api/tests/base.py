from cinemanio.api.tests.helpers import execute
from cinemanio.core.tests.base import BaseTestCase


class ListQueryBaseTestCase(BaseTestCase):
    factory = None
    type = None
    count = 100

    def setUp(self):
        for i in range(self.count):
            self.factory()

    def assertCountNonZeroAndEqual(self, result, count):
        self.assertGreater(count, 0)
        self.assertEqual(len(result[self.type]['edges']), count)

    def populated_cursors(self, cursors, result):
        for cursor in result[self.type]['edges']:
            cursors.add(cursor['cursor'])

    def assert_pagination(self):
        query = '''
            {
              %s(first: 10, after: "%s") {
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
            '''
        # TODO: remove one extra SELECT COUNT(*) AS "__count" FROM "core_movie"
        with self.assertNumQueries(3):
            result = execute(query % (self.type, ''))
        self.assertCountNonZeroAndEqual(result, 10)
        self.assertEqual(result[self.type]['totalCount'], self.count)

        cursors = set()
        self.populated_cursors(cursors, result)

        for i in range(10):
            query_paginated = query % (self.type, result[self.type]['pageInfo']['endCursor'])
            if i == 9:
                with self.assertNumQueries(2):
                    result = execute(query_paginated)
                self.assertEqual(len(result[self.type]['edges']), 0)
            else:
                with self.assertNumQueries(3):
                    result = execute(query_paginated)
                self.assertCountNonZeroAndEqual(result, 10)
                self.populated_cursors(cursors, result)

        self.assertEqual(len(cursors), self.count)
