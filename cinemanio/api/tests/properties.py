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
            {
              %s {
                id, name
              }
            }
            ''' % fieldname
        with self.assertNumQueries(1):
            result = execute(query)
        self.assertEqual(len(result[fieldname]), model.objects.count())
