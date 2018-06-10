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
from cinemanio.relations.signals import relation_changed


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

    relation_query = '''
        query %s($id: ID!) {
          %s(id: $id) {
            relation {
              ...RelationFields
            }
            relationsCount {
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

    def setUp(self):
        self.create_user()

    def get_relate_vars(self, instance, rel):
        model_name = instance.__class__.__name__
        return (f'{model_name}RelationNode', ', '.join(rel.codes),
                f'{model_name}RelationCountNode', ', '.join(rel.codes))

    def get_relation_vars(self, instance, rel):
        model_name = instance.__class__.__name__
        return (model_name,
                model_name.lower(),
                f'{model_name}RelationNode', ', '.join(rel.codes),
                f'{model_name}RelationCountNode', ', '.join(rel.codes))

    def assertRelationAndCounts(self, relation, instance, codes):
        self.assertEqual(relation.objects.count(), 1)
        rel = relation.objects.last()
        self.assertEqual(rel.object, instance)
        self.assertEqual(rel.user, self.user)
        self.assertRelation(rel, codes)

        for code in rel.codes:
            count = getattr(instance.relations_count, code)
            self.assertEqual(count, 1 if code in codes else 0)

    def assertResponseRelationAndCounts(self, relation, relation_count, rel, codes):
        for code in rel.codes:
            self.assertEqual(relation[code], code in codes)
            self.assertEqual(relation_count[code], 1 if code in codes else 0)

    @parameterized.expand([
        (MovieFactory, MovieNode, MovieRelation, ['fav', 'like', 'seen'], 23),
        (PersonFactory, PersonNode, PersonRelation, ['fav', 'like'], 19),
    ])
    def test_relate_first_time(self, factory, node, relation, codes, queries_count):
        instance = factory()
        self.assertEqual(relation.objects.count(), 0)

        with self.assertNumQueries(7 + queries_count):
            result = execute(self.relate_mutation % self.get_relate_vars(instance, relation()),
                             dict(id=to_global_id(node._meta.name, instance.id), type='fav'),
                             self.context)

        self.assertResponseRelationAndCounts(result['relate']['relation'],
                                             result['relate']['count'], relation(), codes)
        self.assertRelationAndCounts(relation, instance, codes)

    @parameterized.expand([
        (MovieRelationFactory, MovieNode, MovieRelation, ['like', 'seen'], 24),
        (PersonRelationFactory, PersonNode, PersonRelation, ['like'], 20),
    ])
    def test_change_relation(self, factory, node, relation, codes, queries_count):
        fav_codes = codes + ['fav']
        rel = factory(user=self.user, **{code: True for code in fav_codes})
        instance = rel.object
        self.assertEqual(relation.objects.count(), 1)
        self.assertRelation(rel, fav_codes)

        with self.assertNumQueries(4 + queries_count):
            result = execute(self.relate_mutation % self.get_relate_vars(instance, rel),
                             dict(id=to_global_id(node._meta.name, instance.id), type='fav'),
                             self.context)

        self.assertResponseRelationAndCounts(result['relate']['relation'],
                                             result['relate']['count'], rel, codes)

        self.assertRelationAndCounts(relation, instance, codes)

    @parameterized.expand([
        (MovieRelationFactory, MovieNode, ['fav', 'like', 'seen']),
        (PersonRelationFactory, PersonNode, ['fav', 'like']),
    ])
    def test_object_with_relation(self, factory, node, codes):
        rel = factory(user=self.user, **{code: True for code in codes})
        relation_changed.send(sender=rel.__class__, instance=rel)
        instance = rel.object

        with self.assertNumQueries(2):
            result = execute(self.relation_query % self.get_relation_vars(instance, rel),
                             dict(id=to_global_id(node._meta.name, instance.id)),
                             self.context)

        query_name = instance.__class__.__name__.lower()
        self.assertResponseRelationAndCounts(result[query_name]['relation'],
                                             result[query_name]['relationsCount'], rel, codes)
