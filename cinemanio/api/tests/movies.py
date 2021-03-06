from parameterized import parameterized

from cinemanio.api.helpers import global_id
from cinemanio.api.schema.properties import GenreNode, CountryNode, LanguageNode
from cinemanio.api.tests.base import ListQueryBaseTestCase
from cinemanio.core.factories import MovieFactory
from cinemanio.core.models import Movie, Genre, Country, Language


class MoviesQueryTestCase(ListQueryBaseTestCase):
    def setUp(self):
        for i in range(self.count):
            MovieFactory()

    def test_movies_query(self):
        query = '''
            query Movies {
              movies {
                edges {
                  node {
                    id
                    prequelFor { id }
                    genres { id }
                    countries { id }
                    languages { id }
                  }
                }
              }
            }
        '''
        with self.assertNumQueries(5):
            result = self.execute(query)
        self.assert_count_equal(result['movies'], self.count)

    def test_movies_query_fragments(self):
        query = '''
            query Movies {
              movies {
                edges {
                  node {
                    year, runtime
                    prequelFor { year, runtime }
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
              genres { nameEn }
            }
            fragment MovieInfoCountries on MovieNode {
              countries { nameEn }
            }
            fragment MovieInfoLanguages on MovieNode {
              languages { nameEn }
            }
        '''
        with self.assertNumQueries(5):
            result = self.execute(query)
        self.assert_count_equal(result['movies'], self.count)

    def test_movies_filter_by_year_range(self):
        query = '''
            query Movies($min: Float!, $max: Float!) {
              movies(year_Gte: $min, year_Lte: $max) {
                edges {
                  node {
                    id
                    year
                  }
                }
              }
            }
        '''
        with self.assertNumQueries(2):
            result = self.execute(query, dict(min=1940, max=1980))
        self.assert_count_equal(result['movies'], Movie.objects.filter(year__gte=1940, year__lte=1980).count())
        for movie in result['movies']['edges']:
            assert movie['node']['year'] >= 1940
            assert movie['node']['year'] <= 1980

    @parameterized.expand([
        (Genre, GenreNode, 'genres'),
        (Country, CountryNode, 'countries'),
        (Language, LanguageNode, 'languages'),
    ])
    def test_movies_filter_by_m2m(self, model, node, fieldname):
        items = model.objects.all()[:2]
        item1, item2 = items
        for m in Movie.objects.all()[:10]:
            getattr(m, fieldname).set(items)
        query = '''
            query Movies($rels: [ID!]) {
              movies(%s: $rels) {
                edges {
                  node {
                    id
                  }
                }
              }
            }
        ''' % fieldname
        # TODO: decrease number of queries by 1
        with self.assertNumQueries(3):
            result = self.execute(query, dict(rels=(global_id(item1), global_id(item2))))
        self.assert_count_equal(result['movies'], (Movie.objects
                                                   .filter(**{fieldname: item1})
                                                   .filter(**{fieldname: item2}).count()))

    def test_movies_filter_by_wrong_m2m(self):
        query = '''
            query Movies($rels: [ID!]) {
              movies(countries: $rels) {
                edges {
                  node {
                    id
                  }
                }
              }
            }
        '''
        with self.assertRaises(AssertionError):
            self.execute(query, dict(rels=(global_id(Genre(id=1)), global_id(Country(id=1)))))

    def test_movies_order(self):
        query = '''
            query Movies($order: String!) {
              movies(orderBy: $order) {
                edges {
                  node {
                    year
                  }
                }
              }
            }
        '''
        self.assert_response_orders(query, 'movies', order_by='year', queries_count=2, model=Movie,
                                    get_value_instance=lambda n: n.year,
                                    get_value_result=lambda n: n['year'])
