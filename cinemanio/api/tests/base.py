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
        '''
        # TODO: remove one extra SELECT COUNT(*) AS "__count" FROM "core_movie"
        with self.assertNumQueries(3):
            result = execute(query % self.type, dict(after=''))
        self.assertCountNonZeroAndEqual(result, 10)
        self.assertEqual(result[self.type]['totalCount'], self.count)

        cursors = set()
        self.populated_cursors(cursors, result)

        for i in range(10):
            query_paginated = query % self.type
            values = dict(after=result[self.type]['pageInfo']['endCursor'])
            if i == 9:
                with self.assertNumQueries(2):
                    result = execute(query_paginated, values)
                self.assertEqual(len(result[self.type]['edges']), 0)
            else:
                with self.assertNumQueries(3):
                    result = execute(query_paginated, values)
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
        for i in range(10):
            ImageLinkFactory(object=m, image__type=image_type)
        query = '''
            query Object($id: ID!) {
              %s(id: $id) {
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
        ''' % self.type
        # TODO: reduce number of queries
        with self.assertNumQueries(3 + (4 * 10)):
            result = execute(query, dict(id=to_global_id(self.node._meta.name, m.id)))
        self.assertEqual(len(result[self.type]['images']['edges']), m.images.count())
        first = result[self.type]['images']['edges'][0]['node']['image']
        self.assertEqual(first['type'], image_type.name)
        self.assertTrue(len(first['original']) > 0)
        self.assertTrue(len(first['icon']) > 0)

    def assertRandomImage(self, image_type, field):
        m = self.factory()
        query = '''
            query Object($id: ID!) {
              %s(id: $id) {
                id
                %s {
                  type
                  original
                  fullCard
                  shortCard
                  detail
                  icon
                }
              }
            }
        ''' % (self.type, field)
        values = dict(id=to_global_id(self.node._meta.name, m.id))

        # no images
        with self.assertNumQueries(3):
            result_nothing = execute(query, values)
        self.assertEqual(result_nothing[self.type][field], None)

        # images
        for i in range(100):
            ImageLinkFactory(object=m, image__type=image_type)

        with self.assertNumQueries(3 + 4):
            result = execute(query, values)
        self.assertEqual(result[self.type][field]['type'], image_type.name)
        self.assertTrue(len(result[self.type][field]['original']) > 0)

        # try again and compare
        result_another = execute(query, values)
        self.assertNotEqual(result[self.type][field]['original'], result_another[self.type][field]['original'])
