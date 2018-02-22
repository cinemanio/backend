from graphql_relay.node.node import to_global_id

from cinemanio.api.schema.properties import GenreNode
from cinemanio.api.tests.helpers import execute
from cinemanio.core.factories import MovieFactory
from cinemanio.core.models import Movie
from cinemanio.api.tests.base import ListQueryBaseTestCase


class MoviesQueryTestCase(ListQueryBaseTestCase):
    factory = MovieFactory
    type = 'movies'

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
        self.assertCountNonZeroAndEqual(result, self.count)

    def test_movies_pagination(self):
        self.assert_pagination()

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
