from graphql_relay.node.node import to_global_id
from parameterized import parameterized

from cinemanio.api.schema.movie import MovieNode
from cinemanio.api.schema.person import PersonNode
from cinemanio.api.tests.base import UserQueryBaseTestCase
from cinemanio.api.tests.helpers import execute
from cinemanio.core.factories import MovieFactory, PersonFactory
from cinemanio.relations.factories import MovieRelationFactory, PersonRelationFactory
from cinemanio.relations.models import MovieRelation, PersonRelation
from cinemanio.relations.tests import RelationsTestMixin


class RelationsTestCase(UserQueryBaseTestCase, RelationsTestMixin):
    relate_mutation = '''
        mutation Relate($id: ID!, $type: String!) {
          relate(id: $id, type: $type) {
            relation {
              ...RelationFields
            }
            count {
              ...RelationCountFields
            }
          }
        }
        fragment RelationFields on %s {
          %s
        }
        fragment RelationCountFields on %s {
          %s
        }
    '''

    def assertRelationAndCounts(self, relation, instance, codes):
        self.assertEqual(relation.objects.count(), 1)
        rel = relation.objects.last()
        self.assertEqual(rel.object, instance)
        self.assertEqual(rel.user, self.user)
        self.assertRelation(rel, codes)

        for code in rel.codes:
            count = getattr(instance.relations_count, code)
            self.assertEqual(count, 1 if code in codes else 0)

    def get_vars(self, instance, codes):
        model_name = instance.__class__.__name__
        return (f'{model_name}RelationNode', ', '.join(codes),
                f'{model_name}RelationCountNode', ', '.join(codes))

    @parameterized.expand([
        (MovieFactory, MovieNode, MovieRelation, ['fav', 'like', 'seen'], 23),
        (PersonFactory, PersonNode, PersonRelation, ['fav', 'like'], 19),
    ])
    def test_relate_first_time(self, factory, node, relation, codes, queries_count):
        instance = factory()
        self.create_user()
        self.assertEqual(relation.objects.count(), 0)

        with self.assertNumQueries(7 + queries_count):
            result = execute(self.relate_mutation % self.get_vars(instance, codes),
                             dict(id=to_global_id(node._meta.name, instance.id), type='fav'),
                             self.context)
        for code in codes:
            self.assertEqual(result['relate']['relation'][code], True)
            self.assertEqual(result['relate']['count'][code], 1)

        self.assertRelationAndCounts(relation, instance, codes)

    @parameterized.expand([
        (MovieRelationFactory, MovieNode, MovieRelation, ['like', 'seen'], 24),
        (PersonRelationFactory, PersonNode, PersonRelation, ['like'], 20),
    ])
    def test_change_relation(self, factory, node, relation, codes, queries_count):
        self.create_user()
        fav_codes = codes + ['fav']
        rel = factory(user=self.user, **{code: True for code in fav_codes})
        instance = rel.object
        self.assertEqual(relation.objects.count(), 1)
        self.assertRelation(rel, fav_codes)

        with self.assertNumQueries(4 + queries_count):
            result = execute(self.relate_mutation % self.get_vars(instance, fav_codes),
                             dict(id=to_global_id(node._meta.name, instance.id), type='fav'),
                             self.context)
        self.assertEqual(result['relate']['relation']['fav'], False)
        self.assertEqual(result['relate']['count']['fav'], 0)
        for code in codes:
            self.assertEqual(result['relate']['relation'][code], True)
            self.assertEqual(result['relate']['count'][code], 1)

        self.assertRelationAndCounts(relation, instance, codes)
