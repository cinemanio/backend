from unittest import skip

from graphql_relay.node.node import to_global_id
from parameterized import parameterized

from cinemanio.api.schema.properties import CountryNode, RoleNode
from cinemanio.api.tests.base import ListQueryBaseTestCase
from cinemanio.core.factories import PersonFactory
from cinemanio.core.models import Person, Role


class PersonsQueryTestCase(ListQueryBaseTestCase):
    count = 100

    def setUp(self):
        for i in range(self.count):
            PersonFactory()

    def test_persons_query(self):
        query = '''
            query Persons {
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
            result = self.execute(query)
        self.assertCountNonZeroAndEqual(result['persons'], self.count)

    @skip('add this filter to filterset')
    def test_persons_query_filter_by_birth_year(self):
        year = Person.objects.all()[0].date_birth.year
        query = '''
            query Persons($year: Float!) {
              persons(dateBirth_Year: $year) {
                edges {
                  node {
                    name
                  }
                }
              }
            }
        '''
        with self.assertNumQueries(2):
            result = self.execute(query, dict(year=year))
        self.assertCountNonZeroAndEqual(result['persons'], Person.objects.filter(date_birth__year=year).count())

    def test_persons_query_filter_by_country(self):
        country = Person.objects.all()[0].country
        query = '''
            query Persons($country: ID!) {
              persons(country: $country) {
                edges {
                  node {
                    name
                  }
                }
              }
            }
        '''
        with self.assertNumQueries(2):
            result = self.execute(query, dict(country=to_global_id(CountryNode._meta.name, country.id)))
        self.assertCountNonZeroAndEqual(result['persons'], Person.objects.filter(country=country).count())

    @parameterized.expand([(Role, 'roles')])
    def test_movies_filter_by_m2m(self, model, fieldname):
        items = model.objects.all()[:2]
        item1, item2 = items
        for m in Person.objects.all()[:10]:
            getattr(m, fieldname).set(items)
        query = '''
            query Persons($rels: [ID!]) {
              persons(%s: $rels) {
                edges {
                  node {
                    name
                  }
                }
              }
            }
        ''' % fieldname
        # TODO: decrease number of queries by 1
        with self.assertNumQueries(3):
            result = self.execute(query, dict(rels=[to_global_id(RoleNode._meta.name, item1.id),
                                                    to_global_id(RoleNode._meta.name, item2.id)]))
        self.assertCountNonZeroAndEqual(result['persons'], (Person.objects
                                                            .filter(**{fieldname: item1})
                                                            .filter(**{fieldname: item2}).count()))
