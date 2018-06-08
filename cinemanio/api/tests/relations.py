from graphql_relay.node.node import to_global_id
from parameterized import parameterized

from cinemanio.api.schema.movie import MovieNode
from cinemanio.api.schema.person import PersonNode
from cinemanio.api.tests.base import UserQueryBaseTestCase
from cinemanio.api.tests.helpers import execute
from cinemanio.core.factories import MovieFactory, PersonFactory
from cinemanio.relations.models import MovieRelation, PersonRelation
from cinemanio.relations.tests import RelationsTestMixin
from cinemanio.relations.factories import MovieRelationFactory, PersonRelationFactory


class RelationsTestCase(UserQueryBaseTestCase, RelationsTestMixin):
    relate_mutation = '''
        mutation Relate($id: ID!, $type: String!) {
          relate(id: $id, type: $type) {
            ok
          }
        }
    '''

    @parameterized.expand([
        (MovieFactory, MovieNode, MovieRelation, ['fav', 'like', 'seen']),
        (PersonFactory, PersonNode, PersonRelation, ['fav', 'like']),
    ])
    def test_relate_first_time(self, factory, node, relation, codes):
        instance = factory()
        self.create_user()
        self.assertEqual(relation.objects.count(), 0)

        with self.assertNumQueries(6):
            result = execute(self.relate_mutation,
                             dict(id=to_global_id(node._meta.name, instance.id), type='fav'),
                             self.context)
        self.assertTrue(result['relate']['ok'])

        # relation
        self.assertEqual(relation.objects.count(), 1)
        rel = relation.objects.last()
        self.assertEqual(rel.object, instance)
        self.assertEqual(rel.user, self.user)
        self.assertRelation(rel, codes)

    @parameterized.expand([
        (MovieRelationFactory, MovieNode, MovieRelation, ['like', 'seen']),
        (PersonRelationFactory, PersonNode, PersonRelation, ['like']),
    ])
    def test_change_relation(self, factory, node, relation, codes):
        self.create_user()
        rel = factory(user=self.user, **{code: True for code in codes + ['fav']})
        instance = rel.object
        self.assertEqual(relation.objects.count(), 1)
        self.assertRelation(rel, codes + ['fav'])

        with self.assertNumQueries(3):
            result = execute(self.relate_mutation,
                             dict(id=to_global_id(node._meta.name, instance.id), type='fav'),
                             self.context)
        self.assertTrue(result['relate']['ok'])

        # relation
        self.assertEqual(relation.objects.count(), 1)
        rel = relation.objects.last()
        self.assertEqual(rel.object, instance)
        self.assertEqual(rel.user, self.user)
        self.assertRelation(rel, codes)
