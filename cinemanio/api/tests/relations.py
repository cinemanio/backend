from graphql_relay.node.node import to_global_id
from parameterized import parameterized

from cinemanio.api.schema.movie import MovieNode
from cinemanio.api.schema.person import PersonNode
from cinemanio.api.tests.base import QueryBaseTestCase
from cinemanio.core.factories import MovieFactory, PersonFactory
from cinemanio.relations.factories import MovieRelationFactory, PersonRelationFactory
from cinemanio.relations.models import MovieRelation, PersonRelation
from cinemanio.relations.signals import relation_changed
from cinemanio.relations.tests import RelationsTestMixin


class RelationsQueryTestCase(QueryBaseTestCase, RelationsTestMixin):
    relate_mutation = '''
        mutation Relate($id: ID!, $code: String!) {
          relate(id: $id, code: $code) {
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

    object_relation_query = '''
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

    objects_relation_query = '''
        query %s {
          %s {
            edges {
              node {
                relation {
                  ...RelationFields
                }
                relationsCount {
                  ...RelationCountFields
                }
              }
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

    def get_relate_vars(self, rel):
        model_name = rel.object.__class__.__name__
        return (f'{model_name}RelationNode', ', '.join(rel.codes),
                f'{model_name}RelationCountNode', ', '.join(rel.codes))

    def get_object_vars(self, rel):
        model_name = rel.object.__class__.__name__
        return (model_name,
                model_name.lower(),
                f'{model_name}RelationNode', ', '.join(rel.codes),
                f'{model_name}RelationCountNode', ', '.join(rel.codes))

    def get_objects_vars(self, rel):
        model_name = rel.object.__class__.__name__
        return (model_name + 's',
                model_name.lower() + 's',
                f'{model_name}RelationNode', ', '.join(rel.codes),
                f'{model_name}RelationCountNode', ', '.join(rel.codes))

    def create_relation(self, factory, **kwargs):
        rel = factory(user=self.user, **kwargs)
        relation_changed.send(sender=rel.__class__, instance=rel)
        return rel

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

    def assertUnauthResponseRelationAndCounts(self, relation, relation_count, rel, codes):
        for code in rel.codes:
            self.assertEqual(relation[code], False)
            self.assertEqual(relation_count[code], 1 if code in codes else 0)

    @parameterized.expand([
        (MovieFactory, MovieNode, MovieRelation, ['fav', 'like', 'seen'], 23),
        (PersonFactory, PersonNode, PersonRelation, ['fav', 'like'], 19),
    ])
    def test_relate_first_time(self, factory, node, relation, codes, queries_count):
        instance = factory()
        rel = relation(object=instance)
        self.assertEqual(relation.objects.count(), 0)

        with self.assertNumQueries(7 + queries_count):
            result = self.execute(self.relate_mutation % self.get_relate_vars(rel),
                                  dict(id=to_global_id(node._meta.name, instance.id), code='fav'),
                                  self.context)

        self.assertResponseRelationAndCounts(result['relate']['relation'],
                                             result['relate']['count'], relation(), codes)
        self.assertRelationAndCounts(relation, instance, codes)

    @parameterized.expand([
        (MovieRelationFactory, MovieNode, MovieRelation, ['like', 'seen'], 19),
        (PersonRelationFactory, PersonNode, PersonRelation, ['like'], 15),
    ])
    def test_change_relation(self, factory, node, relation, codes, queries_count):
        fav_codes = codes + ['fav']
        rel = self.create_relation(factory, **{code: True for code in fav_codes})
        self.assertEqual(relation.objects.count(), 1)
        self.assertRelation(rel, fav_codes)

        with self.assertNumQueries(4 + queries_count):
            result = self.execute(self.relate_mutation % self.get_relate_vars(rel),
                                  dict(id=to_global_id(node._meta.name, rel.object.id), code='fav'),
                                  self.context)

        self.assertResponseRelationAndCounts(result['relate']['relation'],
                                             result['relate']['count'], rel, codes)

        self.assertRelationAndCounts(relation, rel.object, codes)

    @parameterized.expand([
        (MovieRelationFactory, MovieNode, ['fav', 'like', 'seen']),
        (PersonRelationFactory, PersonNode, ['fav', 'like']),
    ])
    def test_object_relation(self, factory, node, codes):
        rel = self.create_relation(factory, **{code: True for code in codes})
        query_name = rel.object.__class__.__name__.lower()

        with self.assertNumQueries(2):
            result = self.execute(self.object_relation_query % self.get_object_vars(rel),
                                  dict(id=to_global_id(node._meta.name, rel.object.id)),
                                  self.context)

        self.assertResponseRelationAndCounts(result[query_name]['relation'],
                                             result[query_name]['relationsCount'], rel, codes)

    @parameterized.expand([
        (MovieFactory, MovieNode, MovieRelation),
        (PersonFactory, PersonNode, PersonRelation),
    ])
    def test_object_no_relation(self, factory, node, relation):
        instance = factory()
        rel = relation(object=instance)
        query_name = instance.__class__.__name__.lower()

        with self.assertNumQueries(2):
            result = self.execute(self.object_relation_query % self.get_object_vars(rel),
                                  dict(id=to_global_id(node._meta.name, instance.id)),
                                  self.context)

        self.assertResponseRelationAndCounts(result[query_name]['relation'],
                                             result[query_name]['relationsCount'], relation(), [])

    @parameterized.expand([
        (MovieRelationFactory, MovieNode, ['fav', 'like', 'seen']),
        (PersonRelationFactory, PersonNode, ['fav', 'like']),
    ])
    def test_object_relation_unauth(self, factory, node, codes):
        rel = self.create_relation(factory, **{code: True for code in codes})
        query_name = rel.object.__class__.__name__.lower()

        with self.assertNumQueries(1):
            result = self.execute(self.object_relation_query % self.get_object_vars(rel),
                                  dict(id=to_global_id(node._meta.name, rel.object.id)),
                                  self.Context(user=None))

        self.assertUnauthResponseRelationAndCounts(result[query_name]['relation'],
                                                   result[query_name]['relationsCount'], rel, codes)

    @parameterized.expand([
        (MovieRelationFactory, MovieNode, ['fav', 'like', 'seen']),
        (PersonRelationFactory, PersonNode, ['fav', 'like']),
    ])
    def test_objects_relation(self, factory, node, codes):
        for i in range(100):
            rel = self.create_relation(factory, **{code: True for code in codes})
            query_name = rel.object.__class__.__name__.lower() + 's'

        with self.assertNumQueries(3):
            result = self.execute(self.objects_relation_query % self.get_objects_vars(rel),
                                  None,
                                  self.context)

        self.assertEqual(len(result[query_name]['edges']), 100)
        for obj in result[query_name]['edges']:
            self.assertResponseRelationAndCounts(obj['node']['relation'],
                                                 obj['node']['relationsCount'], rel, codes)

    @parameterized.expand([
        (MovieFactory, MovieRelation),
        (PersonFactory, PersonRelation),
    ])
    def test_objects_no_relation(self, factory, relation):
        for i in range(100):
            instance = factory()
            query_name = instance.__class__.__name__.lower() + 's'
        rel = relation(object=instance)

        with self.assertNumQueries(3):
            result = self.execute(self.objects_relation_query % self.get_objects_vars(rel),
                                  None,
                                  self.context)

        self.assertEqual(len(result[query_name]['edges']), 100)
        for obj in result[query_name]['edges']:
            self.assertResponseRelationAndCounts(obj['node']['relation'],
                                                 obj['node']['relationsCount'], rel, [])

    @parameterized.expand([
        (MovieRelationFactory, ['fav', 'like', 'seen']),
        (PersonRelationFactory, ['fav', 'like']),
    ])
    def test_objects_relation_unauth(self, factory, codes):
        for i in range(100):
            rel = self.create_relation(factory, **{code: True for code in codes})
            query_name = rel.object.__class__.__name__.lower() + 's'

        with self.assertNumQueries(2):
            result = self.execute(self.objects_relation_query % self.get_objects_vars(rel),
                                  None,
                                  self.Context(user=None))

        self.assertEqual(len(result[query_name]['edges']), 100)
        for obj in result[query_name]['edges']:
            self.assertUnauthResponseRelationAndCounts(obj['node']['relation'],
                                                       obj['node']['relationsCount'], rel, codes)
