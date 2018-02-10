from graphql_relay.node.node import to_global_id

from cinemanio.api.schema.movie import MovieNode
from cinemanio.api.tests.helpers import execute
from cinemanio.core.factories import MovieFactory
from cinemanio.core.tests.base import BaseTestCase


class MovieQueryTestCase(BaseTestCase):
    def assertM2MRel(self, result, queryset, fieldname='name'):
        self.assertListEqual([r[fieldname] for r in result], list(queryset.values_list('name', flat=True)))

    def test_movie(self):
        m = MovieFactory()
        query = '''
            {
              movie(id: "%s") {
                title, year, runtime
                genres { name }
                countries { name }
                languages { name }
              }
            }
            ''' % to_global_id(MovieNode._meta.name, m.id)
        with self.assertNumQueries(4):
            result = execute(query)
        self.assertEqual(result['movie']['title'], m.title)
        self.assertEqual(result['movie']['year'], m.year)
        self.assertEqual(result['movie']['runtime'], m.runtime)
        self.assertGreater(len(result['movie']['genres']), 0)
        self.assertM2MRel(result['movie']['genres'], m.genres)
        self.assertM2MRel(result['movie']['languages'], m.languages)
        self.assertM2MRel(result['movie']['countries'], m.countries)

    def test_movie_with_related_movie(self):
        m = MovieFactory(prequel_for=MovieFactory(), sequel_for=MovieFactory(), remake_for=MovieFactory())
        query = '''
            {
              movie(id: "%s") {
                title, year, runtime
                prequelFor { title, year, runtime }
                sequelFor { title, year, runtime }
                remakeFor { title, year, runtime }
              }
            }
            ''' % to_global_id(MovieNode._meta.name, m.id)
        with self.assertNumQueries(1):
            result = execute(query)
        self.assertEqual(result['movie']['title'], m.title)
        self.assertEqual(result['movie']['year'], m.year)
        self.assertEqual(result['movie']['runtime'], m.runtime)
        self.assertEqual(result['movie']['prequelFor']['title'], m.prequel_for.title)
        self.assertEqual(result['movie']['prequelFor']['year'], m.prequel_for.year)
        self.assertEqual(result['movie']['prequelFor']['runtime'], m.prequel_for.runtime)
        self.assertEqual(result['movie']['sequelFor']['title'], m.sequel_for.title)
        self.assertEqual(result['movie']['sequelFor']['year'], m.sequel_for.year)
        self.assertEqual(result['movie']['sequelFor']['runtime'], m.sequel_for.runtime)
        self.assertEqual(result['movie']['remakeFor']['title'], m.remake_for.title)
        self.assertEqual(result['movie']['remakeFor']['year'], m.remake_for.year)
        self.assertEqual(result['movie']['remakeFor']['runtime'], m.remake_for.runtime)
