from unittest import skip

from parameterized import parameterized

from cinemanio.api.helpers import global_id
from cinemanio.api.schema.properties import RoleNode
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
                    id
                    country { nameEn }
                  }
                }
              }
            }
        '''
        with self.assertNumQueries(2):
            result = self.execute(query)
        self.assert_count_equal(result['persons'], self.count)

    @skip('add this filter to filterset')
    def test_persons_query_filter_by_birth_year(self):
        year = Person.objects.all()[0].date_birth.year
        query = '''
            query Persons($year: Float!) {
              persons(dateBirth_Year: $year) {
                edges {
                  node {
                    id
                  }
                }
              }
            }
        '''
        with self.assertNumQueries(2):
            result = self.execute(query, dict(year=year))
        self.assert_count_equal(result['persons'], Person.objects.filter(date_birth__year=year).count())

    def test_persons_query_filter_by_country(self):
        country = Person.objects.all()[0].country
        query = '''
            query Persons($country: ID!) {
              persons(country: $country) {
                edges {
                  node {
                    id
                  }
                }
              }
            }
        '''
        with self.assertNumQueries(2):
            result = self.execute(query, dict(country=global_id(country)))
        self.assert_count_equal(result['persons'], Person.objects.filter(country=country).count())

    @parameterized.expand([(Role, RoleNode, 'roles')])
    def test_movies_filter_by_m2m(self, model, node, fieldname):
        items = model.objects.all()[:2]
        item1, item2 = items
        for m in Person.objects.all()[:10]:
            getattr(m, fieldname).set(items)
        query = '''
            query Persons($rels: [ID!]) {
              persons(%s: $rels) {
                edges {
                  node {
                    id
                  }
                }
              }
            }
        ''' % fieldname
        # TODO: decrease number of queries by 1
        with self.assertNumQueries(3):
            result = self.execute(query, dict(rels=[global_id(item1), global_id(item2)]))
        self.assert_count_equal(result['persons'], (Person.objects
                                                    .filter(**{fieldname: item1})
                                                    .filter(**{fieldname: item2}).count()))
