from graphql_relay.node.node import to_global_id

from cinemanio.api.tests.helpers import execute
from cinemanio.core.tests.base import BaseTestCase
from cinemanio.images.factories import ImageLinkFactory


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

    def assertPagination(self):
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


class ObjectQueryBaseTestCase(BaseTestCase):
    factory = None
    type = None
    node = None

    def assertM2MRel(self, result, queryset, fieldname='name'):
        self.assertListEqual([r[fieldname] for r in result], list(queryset.values_list('name', flat=True)))

    def assertImages(self, image_type):
        m = self.factory()
        for i in range(100):
            ImageLinkFactory(object=m, image__type=image_type, image__original='absolute_path')
        query = '''
            {
              %s(id: "%s") {
                id
                images {
                  edges {
                    node {
                      image {
                        type
                        original
                        fullCard
                        shortCard
                        detail
                        icon
                      }
                    }
                  }
                }
              }
            }
            ''' % (self.type, to_global_id(self.node._meta.name, m.id))
        with self.assertNumQueries(3 + 4):
            result = execute(query)
        self.assertEqual(len(result[self.type]['images']['edges']), m.images.count())
        first = result[self.type]['images']['edges'][0]['node']['image']
        self.assertEqual(first['type'], f'A_{image_type}')  # TODO: fix that
        self.assertEqual(first['original'], 'absolute_path')
        self.assertTrue(len(first['icon']) > 0)
