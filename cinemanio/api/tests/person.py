from graphql_relay.node.node import to_global_id

from cinemanio.api.schema.person import PersonNode
from cinemanio.api.tests.helpers import execute
from cinemanio.core.factories import PersonFactory, CastFactory
from cinemanio.core.tests.base import BaseTestCase


class PersonQueryTestCase(BaseTestCase):
    def test_person(self):
        p = PersonFactory()
        p_id = to_global_id(PersonNode._meta.name, p.id)
        query = '''
            {
              person(id: "%s") {
                id, firstName, lastName, gender
                dateBirth, dateDeath,
                country { name }
              }
            }
            ''' % p_id
        with self.assertNumQueries(1):
            result = execute(query)
        self.assertEqual(result['person']['id'], p_id)
        self.assertEqual(result['person']['firstName'], p.first_name)
        self.assertEqual(result['person']['lastName'], p.last_name)
        self.assertEqual(result['person']['gender'], 'A_%s' % p.gender)  # TODO: fix it
        self.assertEqual(result['person']['dateBirth'], p.date_birth.strftime('%Y-%m-%d'))
        self.assertEqual(result['person']['dateDeath'], p.date_death.strftime('%Y-%m-%d'))
        self.assertEqual(result['person']['country']['name'], p.country.name)

    def test_person_with_career(self):
        p = PersonFactory()
        for i in range(100):
            CastFactory(person=p)
        query = '''
            {
              person(id: "%s") {
                career {
                  name
                  movie { title }
                  role { name }
                }
              }
            }
            ''' % to_global_id(PersonNode._meta.name, p.id)
        with self.assertNumQueries(2):
            result = execute(query)
        self.assertEqual(len(result['person']['career']), 100)

        for i in range(100):
            result_career = result['person']['career'][i]
            career = p.career.all()[i]
            self.assertEqual(result_career['movie']['title'], career.movie.title)
            self.assertEqual(result_career['role']['name'], career.role.name)
