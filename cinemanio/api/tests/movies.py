from graphql_relay.node.node import to_global_id
from parameterized import parameterized

from cinemanio.api.tests.base import ListQueryBaseTestCase
from cinemanio.api.schema.properties import GenreNode
from cinemanio.api.tests.helpers import execute
from cinemanio.core.factories import MovieFactory
from cinemanio.core.models import Movie, Genre, Country, Language


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
                    prequelFor { id }
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

    def test_movies_query_fragments(self):
        query = '''
            query {
              movies {
                edges {
                  node {
                    title, year, runtime
                    prequelFor { id }
                    ...MovieShort
                  }
                }
              }
            }
            fragment MovieShort on MovieNode {
              ...MovieInfoGenres
              ...MovieInfoCountries
              ...MovieInfoLanguages
            }            
            fragment MovieInfoGenres on MovieNode {
              genres { name }
            }
            fragment MovieInfoCountries on MovieNode {
              countries { name }
            }
            fragment MovieInfoLanguages on MovieNode {
              languages { name }
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

    @parameterized.expand([
        (Genre, 'genres'),
        (Country, 'countries'),
        (Language, 'languages'),
    ])
    def test_movies_filter_by_m2m(self, model, fieldname):
        items = model.objects.all()[:2]
        item1, item2 = items
        for m in Movie.objects.all()[:10]:
            getattr(m, fieldname).set(items)
        query = '''
            {
              movies(%s: ["%s", "%s"]) {
                edges {
                  node {
                    title
                  }
                }
              }
            }
            ''' % (fieldname,
                   to_global_id(GenreNode._meta.name, item1.id),
                   to_global_id(GenreNode._meta.name, item2.id))
        # TODO: decrease number of queries by 1
        with self.assertNumQueries(3):
            result = execute(query)
        self.assertCountNonZeroAndEqual(result, (Movie.objects
                                                 .filter(**{fieldname: item1})
                                                 .filter(**{fieldname: item2}).count()))
