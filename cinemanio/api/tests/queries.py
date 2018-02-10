from unittest import skip

# from django.utils import timezone
from graphql_relay.node.node import to_global_id

from cinemanio.api.schema.movie import MovieNode
from cinemanio.api.schema.properties import GenreType
from cinemanio.core.factories import MovieFactory
from cinemanio.core.models import Movie
from cinemanio.core.tests.base import BaseTestCase
from cinemanio.schema import schema


def execute(query):
    query = '''%s''' % query
    result = schema.execute(query)
    assert not result.errors, result.errors
    return result.data


class MovieGraphqlTestCase(BaseTestCase):
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


class MoviesGraphqlTestCase(BaseTestCase):
    def setUp(self):
        for i in range(100):
            MovieFactory()

    def assertCountNonZeroAndEqual(self, result, count):
        self.assertGreater(count, 0)
        self.assertEqual(len(result['movies']['edges']), count)

    @skip('TODO: fix it')
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
        with self.assertNumQueries(2):
            result = execute(query)
        self.assertCountNonZeroAndEqual(result, Movie.objects.count())

    def test_movies_query_limit(self):
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

    def test_movies_query_filter_by_year(self):
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

    def test_movies_query_filter_by_genre(self):
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
            ''' % to_global_id(GenreType._meta.name, genre.id)
        with self.assertNumQueries(2):
            result = execute(query)
        self.assertCountNonZeroAndEqual(result, Movie.objects.filter(genres__in=[genre]).count())
