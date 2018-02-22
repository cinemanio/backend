from graphql_relay.node.node import to_global_id

from cinemanio.api.schema.properties import CountryNode
from cinemanio.api.tests.helpers import execute
from cinemanio.core.factories import PersonFactory
from cinemanio.core.models import Person
from cinemanio.core.tests.base import BaseTestCase


class PersonsQueryTestCase(BaseTestCase):
    def setUp(self):
        for i in range(100):
            PersonFactory()

    def assertCountNonZeroAndEqual(self, result, count):
        self.assertGreater(count, 0)
        self.assertEqual(len(result['persons']['edges']), count)

    def populated_cursors(self, cursors, result):
        for cursor in result['persons']['edges']:
            cursors.add(cursor['cursor'])

    def test_persons_query(self):
        query = '''
            {
              persons {
                edges {
                  node {
                    firstName, lastName,
                    country { name }
                  }
                }
              }
            }
            '''
        with self.assertNumQueries(2):
            result = execute(query)
        self.assertCountNonZeroAndEqual(result, Person.objects.count())

    def test_persons_pagination(self):
        query = '''
            {
              persons(first: 10%s) {
                totalCount
                edges {
                  node {
                    firstName
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
        # TODO: remove one extra SELECT COUNT(*) AS "__count" FROM "core_person"
        with self.assertNumQueries(3):
            result = execute(query % '')
        self.assertCountNonZeroAndEqual(result, 10)
        self.assertEqual(result['persons']['totalCount'], 100)

        cursors = set()
        self.populated_cursors(cursors, result)

        for i in range(10):
            query_paginated = query % ', after: "{}"'.format(result['persons']['pageInfo']['endCursor'])
            if i == 9:
                with self.assertNumQueries(2):
                    result = execute(query_paginated)
                self.assertEqual(len(result['persons']['edges']), 0)
            else:
                with self.assertNumQueries(3):
                    result = execute(query_paginated)
                self.assertCountNonZeroAndEqual(result, 10)
                self.populated_cursors(cursors, result)

        self.assertEqual(len(cursors), 100)

    def test_persons_query_filter_by_birth_year(self):
        year = Person.objects.all()[0].date_birth.year
        query = '''
            {
              persons(dateBirth_Year: %d) {
                edges {
                  node {
                    firstName
                  }
                }
              }
            }
            ''' % year
        with self.assertNumQueries(2):
            result = execute(query)
        self.assertCountNonZeroAndEqual(result, Person.objects.filter(date_birth__year=year).count())

    def test_persons_query_filter_by_country(self):
        country = Person.objects.all()[0].country
        query = '''
            {
              persons(country: "%s") {
                edges {
                  node {
                    firstName
                  }
                }
              }
            }
            ''' % to_global_id(CountryNode._meta.name, country.id)
        with self.assertNumQueries(2):
            result = execute(query)
        self.assertCountNonZeroAndEqual(result, Person.objects.filter(country=country).count())
