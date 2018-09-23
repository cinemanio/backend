from graphql_relay.node.node import to_global_id

from cinemanio.api.schema.person import PersonNode
from cinemanio.api.schema.properties import RoleNode
from cinemanio.api.tests.base import ObjectQueryBaseTestCase
from cinemanio.core.factories import PersonFactory, CastFactory
from cinemanio.core.models import Gender
from cinemanio.sites.imdb.factories import ImdbPersonFactory
from cinemanio.sites.kinopoisk.factories import KinopoiskPersonFactory


class PersonQueryTestCase(ObjectQueryBaseTestCase):
    def test_person(self):
        p = PersonFactory(gender=Gender.MALE)
        p_id = to_global_id(PersonNode._meta.name, p.id)
        query = '''
            query Person($id: ID!) {
              person(id: $id) {
                id, gender
                nameEn, firstNameEn, lastNameEn
                nameRu, firstNameRu, lastNameRu
                dateBirth, dateDeath
                country { nameEn }
                roles { nameEn }
              }
            }
        '''
        with self.assertNumQueries(2):
            result = self.execute(query, dict(id=p_id))
        self.assertEqual(result['person']['id'], p_id)
        self.assertEqual(result['person']['nameEn'], p.name_en)
        self.assertEqual(result['person']['nameRu'], p.name_ru)
        self.assertEqual(result['person']['gender'], Gender.MALE.name)
        self.assertEqual(result['person']['dateBirth'], p.date_birth.strftime('%Y-%m-%d'))
        self.assertEqual(result['person']['dateDeath'], p.date_death.strftime('%Y-%m-%d'))
        self.assertEqual(result['person']['country']['nameEn'], p.country.name_en)
        self.assertGreater(len(result['person']['roles']), 0)
        self.assert_m2m_rel(result['person']['roles'], p.roles)

    def test_person_with_related_sites(self):
        p = ImdbPersonFactory(person=KinopoiskPersonFactory().person).person
        query = '''
            query Person($id: ID!) {
              person(id: $id) {
                id
                imdb { id, url }
                kinopoisk { id, info, url }
              }
            }
        '''
        with self.assertNumQueries(1):
            result = self.execute(query, dict(id=to_global_id(PersonNode._meta.name, p.id)))
        self.assertEqual(result['person']['imdb']['id'], p.imdb.id)
        self.assertEqual(result['person']['imdb']['url'], p.imdb.url)
        self.assertEqual(result['person']['kinopoisk']['id'], p.kinopoisk.id)
        self.assertEqual(result['person']['kinopoisk']['info'], p.kinopoisk.info)
        self.assertEqual(result['person']['kinopoisk']['url'], p.kinopoisk.url)

    def test_person_without_related_sites(self):
        p = PersonFactory()
        query = '''
            query Person($id: ID!) {
              person(id: $id) {
                id
                imdb { id }
                kinopoisk { id, info }
              }
            }
        '''
        with self.assertNumQueries(1):
            result = self.execute(query, dict(id=to_global_id(PersonNode._meta.name, p.id)))
        self.assertEqual(result['person']['imdb'], None)
        self.assertEqual(result['person']['kinopoisk'], None)

    def test_person_with_career(self):
        p = PersonFactory()
        for i in range(100):
            cast = CastFactory(person=p)
        CastFactory(role=cast.role)
        query = '''
            query Person($id: ID!, $role: ID!) {
              person(id: $id) {
                id
                career(role: $role) {
                  edges {
                    node {
                      name
                      movie { titleEn }
                      role { nameEn }
                    }
                  }
                }
              }
            }
        '''
        with self.assertNumQueries(3):
            result = self.execute(query, dict(id=to_global_id(PersonNode._meta.name, p.id),
                                              role=to_global_id(RoleNode._meta.name, cast.role.id)))
        self.assertEqual(len(result['person']['career']['edges']), p.career.filter(role=cast.role).count())
