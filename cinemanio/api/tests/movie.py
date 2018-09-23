from graphql_relay.node.node import to_global_id

from cinemanio.api.schema.movie import MovieNode
from cinemanio.api.schema.properties import RoleNode
from cinemanio.api.tests.base import ObjectQueryBaseTestCase
from cinemanio.core.factories import MovieFactory, CastFactory
from cinemanio.sites.imdb.factories import ImdbMovieFactory
from cinemanio.sites.kinopoisk.factories import KinopoiskMovieFactory


class MovieQueryTestCase(ObjectQueryBaseTestCase):
    def test_movie_with_m2m(self):
        m = MovieFactory()
        query = '''
            query Movie($id: ID!) {
              movie(id: $id) {
                id
                genres { nameEn }
                countries { nameEn }
                languages { nameEn }
              }
            }
        '''
        with self.assertNumQueries(4):
            result = self.execute(query, dict(id=to_global_id(MovieNode._meta.name, m.id)))
        self.assertGreater(len(result['movie']['genres']), 0)
        self.assertGreater(len(result['movie']['languages']), 0)
        self.assertGreater(len(result['movie']['countries']), 0)
        self.assert_m2m_rel(result['movie']['genres'], m.genres)
        self.assert_m2m_rel(result['movie']['languages'], m.languages)
        self.assert_m2m_rel(result['movie']['countries'], m.countries)

    def test_movie_with_related_movie(self):
        m = MovieFactory(prequel_for=MovieFactory(), sequel_for=MovieFactory(), remake_for=MovieFactory())
        global_id = to_global_id(MovieNode._meta.name, m.id)
        prequel_id = to_global_id(MovieNode._meta.name, m.prequel_for.id)
        sequel_id = to_global_id(MovieNode._meta.name, m.sequel_for.id)
        remake_id = to_global_id(MovieNode._meta.name, m.remake_for.id)
        query = '''
            query Movie($id: ID!) {
              movie(id: $id) {
                id, year
                prequelFor { id, year }
                sequelFor { id, year }
                remakeFor { id, year }
              }
            }
        '''
        with self.assertNumQueries(1):
            result = self.execute(query, dict(id=global_id))
        self.assertEqual(result['movie']['id'], global_id)
        self.assertEqual(result['movie']['prequelFor']['id'], prequel_id)
        self.assertEqual(result['movie']['sequelFor']['id'], sequel_id)
        self.assertEqual(result['movie']['remakeFor']['id'], remake_id)

    def test_movie_with_related_sites(self):
        m = ImdbMovieFactory(movie=KinopoiskMovieFactory().movie).movie
        query = '''
            query Movie($id: ID!) {
              movie(id: $id) {
                id
                imdb { id, rating, votes, url }
                kinopoisk { id, rating, votes, info, url }
              }
            }
        '''
        with self.assertNumQueries(1):
            result = self.execute(query, dict(id=to_global_id(MovieNode._meta.name, m.id)))
        self.assertEqual(result['movie']['imdb']['id'], m.imdb.id)
        self.assertEqual(result['movie']['imdb']['rating'], m.imdb.rating)
        self.assertEqual(result['movie']['imdb']['votes'], m.imdb.votes)
        self.assertEqual(result['movie']['imdb']['url'], m.imdb.url)
        self.assertEqual(result['movie']['kinopoisk']['id'], m.kinopoisk.id)
        self.assertEqual(result['movie']['kinopoisk']['rating'], m.kinopoisk.rating)
        self.assertEqual(result['movie']['kinopoisk']['votes'], m.kinopoisk.votes)
        self.assertEqual(result['movie']['kinopoisk']['info'], m.kinopoisk.info)
        self.assertEqual(result['movie']['kinopoisk']['url'], m.kinopoisk.url)

    def test_movie_without_related_sites(self):
        m = MovieFactory()
        query = '''
            query Movie($id: ID!) {
              movie(id: $id) {
                id
                imdb { id, rating, votes }
                kinopoisk { id, rating, votes, info }
              }
            }
        '''
        with self.assertNumQueries(1):
            result = self.execute(query, dict(id=to_global_id(MovieNode._meta.name, m.id)))
        self.assertEqual(result['movie']['imdb'], None)
        self.assertEqual(result['movie']['kinopoisk'], None)

    def test_movie_with_cast(self):
        m = MovieFactory()
        for i in range(100):
            cast = CastFactory(movie=m)
        CastFactory(role=cast.role)
        query = '''
            query Movie($id: ID!, $role: ID!) {
              movie(id: $id) {
                id
                cast(role: $role) {
                  edges {
                    node {
                      name
                      person { firstNameEn, lastNameEn }
                      role { nameEn }
                    }
                  }
                }
              }
            }
        '''
        with self.assertNumQueries(3):
            result = self.execute(query, dict(id=to_global_id(MovieNode._meta.name, m.id),
                                              role=to_global_id(RoleNode._meta.name, cast.role.id)))
        self.assertEqual(len(result['movie']['cast']['edges']), m.cast.filter(role=cast.role).count())
