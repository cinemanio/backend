from parameterized import parameterized
# from graphql_relay.node.node import to_global_id

# from cinemanio.api.schema.properties import GenreNode
from cinemanio.api.tests.helpers import execute
from cinemanio.core.factories import MovieFactory
from cinemanio.core.models import Movie, Genre, Country, Language
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
            ''' % (fieldname, item1.id, item2.id)
        # TODO: switch to use global ids and decrease number of queries by 1
        # (to_global_id(GenreNode._meta.name, item1.id),
        #  to_global_id(GenreNode._meta.name, item2.id))
        with self.assertNumQueries(3):
            result = execute(query)
        self.assertCountNonZeroAndEqual(result, (Movie.objects
                                                 .filter(**{fieldname: item1})
                                                 .filter(**{fieldname: item2}).count()))
