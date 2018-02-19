from graphql_relay.node.node import to_global_id

from cinemanio.api.schema.properties import GenreNode
from cinemanio.api.tests.helpers import execute
from cinemanio.core.factories import MovieFactory
from cinemanio.core.models import Movie
from cinemanio.core.tests.base import BaseTestCase


class MoviesQueryTestCase(BaseTestCase):
    def setUp(self):
        for i in range(100):
            MovieFactory()

    def assertCountNonZeroAndEqual(self, result, count):
        self.assertGreater(count, 0)
        self.assertEqual(len(result['movies']['edges']), count)

    def test_movies_query(self):
        query = '''
            {
              movies {
                edges {
                  node {
                    title, year, runtime
                    genres { name }
                    countries { name }
                    languages { name }
                  }
                }
              }
            }
            '''
        with self.assertNumQueries(5):
            result = execute(query)
        self.assertCountNonZeroAndEqual(result, Movie.objects.count())

    def test_movies_limit(self):
        query = '''
            {
              movies(first: 10) {
                edges {
                  node {
                    title
                  }
                }
              }
            }
            '''
        with self.assertNumQueries(2):
            result = execute(query)
        self.assertCountNonZeroAndEqual(result, 10)

    def test_movies_filter_by_year(self):
        year = Movie.objects.all()[0].year
        query = '''
            {
              movies(year: %d) {
                edges {
                  node {
                    title
                  }
                }
              }
            }
            ''' % year
        with self.assertNumQueries(2):
            result = execute(query)
        self.assertCountNonZeroAndEqual(result, Movie.objects.filter(year=year).count())

    def test_movies_filter_by_genre(self):
        # TODO: make a filtration by multiple values with AND logic
        # m = Movie.objects.all()[0]
        # genres = Genre.objects.all()[0:2]
        # m.genres.set(genres)
        genre = Movie.objects.all()[0].genres.all()[0]
        query = '''
            {
              movies(genres: "%s") {
                edges {
                  node {
                    title
                  }
                }
              }
            }
            ''' % to_global_id(GenreNode._meta.name, genre.id)
        with self.assertNumQueries(2):
            result = execute(query)
        self.assertCountNonZeroAndEqual(result, Movie.objects.filter(genres__in=[genre]).count())
