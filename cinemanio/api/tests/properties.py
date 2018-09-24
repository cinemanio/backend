from graphql_relay.node.node import from_global_id
from parameterized import parameterized

from cinemanio.core.models import Genre, Country, Language, Role
from cinemanio.api.tests.base import QueryBaseTestCase


class PropertiesQueryTestCase(QueryBaseTestCase):
    @parameterized.expand([
        (Genre, 'genres'),
        (Country, 'countries'),
        (Language, 'languages'),
        (Role, 'roles'),
    ])
    def test_properies_query(self, model, fieldname):
        query = '''
            query Properties {
              %s {
                id, nameEn
              }
            }
        ''' % fieldname
        with self.assertNumQueries(1):
            result = self.execute(query)
        self.assertEqual(len(result[fieldname]), model.objects.count())
        self.assertEqual(result[fieldname][0]['nameEn'], model.objects.all()[0].name_en)
        self.assertEqual(int(from_global_id(result[fieldname][0]['id'])[1]), model.objects.all()[0].id)
