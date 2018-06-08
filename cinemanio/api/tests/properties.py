from graphql_relay.node.node import from_global_id
from parameterized import parameterized

from cinemanio.api.tests.helpers import execute
from cinemanio.core.models import Genre, Country, Language, Role
from cinemanio.core.tests.base import BaseTestCase


class PropertiesQueryTestCase(BaseTestCase):
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
                id, name
              }
            }
        ''' % fieldname
        with self.assertNumQueries(1):
            result = execute(query)
        self.assertEqual(len(result[fieldname]), model.objects.count())
        self.assertEqual(result[fieldname][0]['name'], model.objects.all()[0].name)
        self.assertEqual(int(from_global_id(result[fieldname][0]['id'])[1]), model.objects.all()[0].id)
