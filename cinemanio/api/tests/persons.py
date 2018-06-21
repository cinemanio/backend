from unittest import skip

from graphql_relay.node.node import to_global_id
from parameterized import parameterized

from cinemanio.api.schema.properties import CountryNode, RoleNode
from cinemanio.api.tests.base import ListQueryBaseTestCase
from cinemanio.api.tests.helpers import execute
from cinemanio.core.factories import PersonFactory
from cinemanio.core.models import Person, Role


class PersonsQueryTestCase(ListQueryBaseTestCase):
    factory = PersonFactory
    type = 'persons'

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
        self.assert_count_equal(result, self.count)

    def test_persons_pagination(self):
        self.assert_pagination()

    @skip('add this filter to filterset')
    def test_persons_query_filter_by_birth_year(self):
        year = Person.objects.all()[0].date_birth.year
        query = '''
            {
              persons(dateBirth_Year: %d) {
                edges {
                  node {
                    name
                  }
                }
              }
            }
            ''' % year
        with self.assertNumQueries(2):
            result = execute(query)
        self.assert_count_equal(result, Person.objects.filter(date_birth__year=year).count())

    def test_persons_query_filter_by_country(self):
        country = Person.objects.all()[0].country
        query = '''
            {
              persons(country: "%s") {
                edges {
                  node {
                    name
                  }
                }
              }
            }
            ''' % to_global_id(CountryNode._meta.name, country.id)
        with self.assertNumQueries(2):
            result = execute(query)
        self.assert_count_equal(result, Person.objects.filter(country=country).count())

    @parameterized.expand([(Role, 'roles')])
    def test_movies_filter_by_m2m(self, model, fieldname):
        items = model.objects.all()[:2]
        item1, item2 = items
        for m in Person.objects.all()[:10]:
            getattr(m, fieldname).set(items)
        query = '''
            {
              persons(%s: ["%s", "%s"]) {
                edges {
                  node {
                    name
                  }
                }
              }
            }
            ''' % (fieldname,
                   to_global_id(RoleNode._meta.name, item1.id),
                   to_global_id(RoleNode._meta.name, item2.id))
        # TODO: decrease number of queries by 1
        with self.assertNumQueries(3):
            result = execute(query)
        self.assert_count_equal(result, (Person.objects
                                         .filter(**{fieldname: item1})
                                         .filter(**{fieldname: item2}).count()))
