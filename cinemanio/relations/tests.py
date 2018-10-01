from django.contrib.auth import get_user_model
from django.test import TestCase

from cinemanio.relations.models import MovieRelation
from cinemanio.relations.factories import MovieRelationFactory, PersonRelationFactory
from cinemanio.relations.signals import relation_changed

User = get_user_model()


class RelationsTestMixin:
    def assert_relation(self, rel, codes):
        for code in rel.codes:
            value = getattr(rel, code)
            if code in codes:
                self.assertTrue(value, msg=rel)
            else:
                self.assertFalse(value, msg=rel)


class RelationsFieldsTest(TestCase, RelationsTestMixin):
    def test_relation_change_method(self):
        rel = MovieRelationFactory()
        self.assert_relation(rel, [])
        rel.change("like")
        self.assert_relation(rel, ["seen", "like"])

    def test_movie_relation_change_fav(self):
        rel = MovieRelationFactory(fav=True, like=True, seen=True)
        self.assert_relation(rel, ["fav", "seen", "like"])
        rel.change("fav")
        self.assert_relation(rel, ["seen", "like"])

    def test_movie_relation_fields(self):
        rel = MovieRelationFactory()
        self.assert_relation(rel, [])
        rel.fav = True
        self.assert_relation(rel, ["fav", "seen", "like"])
        rel.fav = False
        self.assert_relation(rel, ["seen", "like"])
        rel.seen = False
        self.assert_relation(rel, [])
        rel.fav = True
        self.assert_relation(rel, ["seen", "like", "fav"])
        rel.dislike = True
        self.assert_relation(rel, ["seen", "dislike"])

    def test_person_relation_fields(self):
        rel = PersonRelationFactory()
        self.assert_relation(rel, [])
        rel.fav = True
        self.assert_relation(rel, ["fav", "like"])
        rel.dislike = True
        self.assert_relation(rel, ["dislike"])
        rel.like = True
        self.assert_relation(rel, ["like"])
        rel.fav = True
        rel.like = False
        self.assert_relation(rel, [])


class RelationsTest(TestCase):
    def test_delete_empty_relations(self):
        """
        Signal should delete records with False relations
        """
        rel = MovieRelationFactory(seen=True)
        relation_changed.send(sender=MovieRelation, instance=rel, code="seen")

        self.assertEqual(MovieRelation.objects.count(), 1)

        rel.seen = False
        rel.save()
        relation_changed.send(sender=MovieRelation, instance=rel, code=None)

        self.assertEqual(MovieRelation.objects.count(), 0)

    def test_user_familiar_objects_count(self):
        rel1 = MovieRelationFactory(seen=True)
        relation_changed.send(sender=MovieRelation, instance=rel1, code="seen")

        count = rel1.user.relations_count
        self.assertEqual(count.movies, 1)

        rel2 = MovieRelationFactory(user=rel1.user, seen=True)
        relation_changed.send(sender=MovieRelation, instance=rel2, code="seen")

        count.refresh_from_db()
        self.assertEqual(count.movies, 2)

        rel1.seen = False
        rel1.save()
        relation_changed.send(sender=MovieRelation, instance=rel1, code=None)

        count.refresh_from_db()
        self.assertEqual(count.movies, 1)

        rel2.seen = False
        rel2.save()
        relation_changed.send(sender=MovieRelation, instance=rel2, code=None)

        count.refresh_from_db()
        self.assertEqual(count.movies, 0)

    def test_object_relations_count(self):
        rel = MovieRelationFactory()
        rel.dislike = True
        rel.save()

        relation_changed.send(sender=MovieRelation, instance=rel)

        count = rel.object.relations_count
        self.assertEqual(rel.object.relations_count.fav, 0)
        self.assertEqual(rel.object.relations_count.like, 0)
        self.assertEqual(rel.object.relations_count.seen, 1)
        self.assertEqual(rel.object.relations_count.dislike, 1)

        for i in range(10):
            rel = MovieRelationFactory(object=rel.object)
            rel.like = True
            rel.save()

        relation_changed.send(sender=MovieRelation, instance=rel)

        count.refresh_from_db()
        self.assertEqual(rel.object.relations_count.fav, 0)
        self.assertEqual(rel.object.relations_count.like, 10)
        self.assertEqual(rel.object.relations_count.seen, 11)
        self.assertEqual(rel.object.relations_count.dislike, 1)
