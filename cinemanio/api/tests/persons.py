from unittest import skip

from graphql_relay.node.node import to_global_id

from cinemanio.api.schema.properties import CountryType
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

    def test_persons_query_limit(self):
        query = '''
            {
              persons(first: 10) {
                edges {
                  node {
                    firstName
                  }
                }
              }
            }
            '''
        with self.assertNumQueries(2):
            result = execute(query)
        self.assertCountNonZeroAndEqual(result, 10)

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
            ''' % to_global_id(CountryType._meta.name, country.id)
        with self.assertNumQueries(2):
            result = execute(query)
        self.assertCountNonZeroAndEqual(result, Person.objects.filter(country=country).count())
