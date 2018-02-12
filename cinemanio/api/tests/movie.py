from graphql_relay.node.node import to_global_id

from cinemanio.api.schema.movie import MovieNode
from cinemanio.api.tests.helpers import execute
from cinemanio.core.factories import MovieFactory
from cinemanio.core.tests.base import BaseTestCase
from cinemanio.sites.imdb.factories import ImdbMovieFactory
from cinemanio.sites.kinopoisk.factories import KinopoiskMovieFactory


class MovieQueryTestCase(BaseTestCase):
    def assertM2MRel(self, result, queryset, fieldname='name'):
        self.assertListEqual([r[fieldname] for r in result], list(queryset.values_list('name', flat=True)))

    def test_movie_with_m2m(self):
        m = MovieFactory()
        query = '''
            {
              movie(id: "%s") {
                genres { name }
                countries { name }
                languages { name }
              }
            }
            ''' % to_global_id(MovieNode._meta.name, m.id)
        with self.assertNumQueries(4):
            result = execute(query)
        self.assertGreater(len(result['movie']['genres']), 0)
        self.assertGreater(len(result['movie']['languages']), 0)
        self.assertGreater(len(result['movie']['countries']), 0)
        self.assertM2MRel(result['movie']['genres'], m.genres)
        self.assertM2MRel(result['movie']['languages'], m.languages)
        self.assertM2MRel(result['movie']['countries'], m.countries)

    def test_movie_with_related_movie(self):
        m = MovieFactory(prequel_for=MovieFactory(), sequel_for=MovieFactory(), remake_for=MovieFactory())
        m_id = to_global_id(MovieNode._meta.name, m.id)
        prequel_id = to_global_id(MovieNode._meta.name, m.prequel_for.id)
        sequel_id = to_global_id(MovieNode._meta.name, m.sequel_for.id)
        remake_id = to_global_id(MovieNode._meta.name, m.remake_for.id)
        query = '''
            {
              movie(id: "%s") {
                id, title, year, runtime
                prequelFor { id, title, year, runtime }
                sequelFor { id, title, year, runtime }
                remakeFor { id, title, year, runtime }
              }
            }
            ''' % m_id
        with self.assertNumQueries(1):
            result = execute(query)
        self.assertEqual(result['movie']['id'], m_id)
        self.assertEqual(result['movie']['title'], m.title)
        self.assertEqual(result['movie']['year'], m.year)
        self.assertEqual(result['movie']['runtime'], m.runtime)
        self.assertEqual(result['movie']['prequelFor']['id'], prequel_id)
        self.assertEqual(result['movie']['prequelFor']['title'], m.prequel_for.title)
        self.assertEqual(result['movie']['prequelFor']['year'], m.prequel_for.year)
        self.assertEqual(result['movie']['prequelFor']['runtime'], m.prequel_for.runtime)
        self.assertEqual(result['movie']['sequelFor']['id'], sequel_id)
        self.assertEqual(result['movie']['sequelFor']['title'], m.sequel_for.title)
        self.assertEqual(result['movie']['sequelFor']['year'], m.sequel_for.year)
        self.assertEqual(result['movie']['sequelFor']['runtime'], m.sequel_for.runtime)
        self.assertEqual(result['movie']['remakeFor']['id'], remake_id)
        self.assertEqual(result['movie']['remakeFor']['title'], m.remake_for.title)
        self.assertEqual(result['movie']['remakeFor']['year'], m.remake_for.year)
        self.assertEqual(result['movie']['remakeFor']['runtime'], m.remake_for.runtime)

    def test_movie_with_related_sites(self):
        m = ImdbMovieFactory(movie=KinopoiskMovieFactory().movie).movie
        query = '''
            {
              movie(id: "%s") {
                title
                imdb {
                  id
                  rating
                  votes
                }
                kinopoisk {
                  id
                  rating
                  votes
                  info
                }
              }
            }
            ''' % to_global_id(MovieNode._meta.name, m.id)
        with self.assertNumQueries(1):
            result = execute(query)
        self.assertEqual(result['movie']['title'], m.title)
        self.assertEqual(result['movie']['imdb']['id'], m.imdb.id)
        self.assertEqual(result['movie']['imdb']['rating'], m.imdb.rating)
        self.assertEqual(result['movie']['imdb']['votes'], m.imdb.votes)
        self.assertEqual(result['movie']['kinopoisk']['id'], m.kinopoisk.id)
        self.assertEqual(result['movie']['kinopoisk']['rating'], m.kinopoisk.rating)
        self.assertEqual(result['movie']['kinopoisk']['votes'], m.kinopoisk.votes)
        self.assertEqual(result['movie']['kinopoisk']['info'], m.kinopoisk.info)

    def test_movie_without_related_sites(self):
        m = MovieFactory()
        query = '''
            {
              movie(id: "%s") {
                title
                imdb {
                  id
                  rating
                  votes
                }
                kinopoisk {
                  id
                  rating
                  votes
                  info
                }
              }
            }
            ''' % to_global_id(MovieNode._meta.name, m.id)
        with self.assertNumQueries(1):
            result = execute(query)
        self.assertEqual(result['movie']['title'], m.title)
        self.assertEqual(result['movie']['imdb'], None)
        self.assertEqual(result['movie']['kinopoisk'], None)
