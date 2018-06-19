from graphql_relay.node.node import to_global_id
from parameterized import parameterized

from cinemanio.api.schema.properties import GenreNode
from cinemanio.api.tests.base import ListQueryBaseTestCase
from cinemanio.core.factories import MovieFactory
from cinemanio.core.models import Movie, Genre, Country, Language


class MoviesQueryTestCase(ListQueryBaseTestCase):
    count = 100

    def setUp(self):
        for i in range(self.count):
            MovieFactory()

    def test_movies_query(self):
        query = '''
            query Movies {
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
            result = self.execute(query)
        self.assertCountNonZeroAndEqual(result['movies'], self.count)

    def test_movies_query_fragments(self):
        query = '''
            query Movies {
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
            result = self.execute(query)
        self.assertCountNonZeroAndEqual(result['movies'], self.count)

    def test_movies_filter_by_year(self):
        year = Movie.objects.all()[0].year
        query = '''
            query Movies($year: Float!) {
              movies(year: $year) {
                edges {
                  node {
                    title
                  }
                }
              }
            }
        '''
        with self.assertNumQueries(2):
            result = self.execute(query, dict(year=year))
        self.assertCountNonZeroAndEqual(result['movies'], Movie.objects.filter(year=year).count())

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
            query Movies($rels: [ID!]) {
              movies(%s: $rels) {
                edges {
                  node {
                    title
                  }
                }
              }
            }
        ''' % fieldname
        # TODO: decrease number of queries by 1
        with self.assertNumQueries(3):
            result = self.execute(query, dict(rels=(to_global_id(GenreNode._meta.name, item1.id),
                                                    to_global_id(GenreNode._meta.name, item2.id))))
        self.assertCountNonZeroAndEqual(result['movies'], (Movie.objects
                                                           .filter(**{fieldname: item1})
                                                           .filter(**{fieldname: item2}).count()))
