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

    def populated_cursors(self, cursors, result):
        for cursor in result['movies']['edges']:
            cursors.add(cursor['cursor'])

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

    def test_movies_pagination(self):
        query = '''
            {
              movies(first: 10%s) {
                totalCount
                edges {
                  node {
                    title
                  }
                  cursor
                }
                pageInfo {
                  endCursor
                  hasNextPage
                }
              }
            }
            '''
        # TODO: remove one extra SELECT COUNT(*) AS "__count" FROM "core_movie"
        with self.assertNumQueries(3):
            result = execute(query % '')
        self.assertCountNonZeroAndEqual(result, 10)
        self.assertEqual(result['movies']['totalCount'], 100)

        cursors = set()
        self.populated_cursors(cursors, result)

        for i in range(10):
            query_paginated = query % ', after: "{}"'.format(result['movies']['pageInfo']['endCursor'])
            if i == 9:
                with self.assertNumQueries(2):
                    result = execute(query_paginated)
                self.assertEqual(len(result['movies']['edges']), 0)
            else:
                with self.assertNumQueries(3):
                    result = execute(query_paginated)
                self.assertCountNonZeroAndEqual(result, 10)
                self.populated_cursors(cursors, result)

        self.assertEqual(len(cursors), 100)

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
