from django.contrib.auth import get_user_model
from django.test import TestCase

from cinemanio.relations.models import MovieRelation, PersonRelation
from cinemanio.relations.factories import MovieRelationFactory
from cinemanio.relations.signals import relation_changed

User = get_user_model()


class RelationsFieldsTest(TestCase):
    def assertAllTrue(self, *args):
        for arg in args:
            self.assertTrue(arg)

    def assertAllFalse(self, *args):
        for arg in args:
            self.assertFalse(arg)

    def test_movie_attitude_fields(self):
        ma = MovieRelation()
        self.assertAllFalse(ma.fav, ma.like, ma.seen, ma.dislike, ma.want, ma.ignore, ma.have)
        ma.like = True
        self.assertAllTrue(ma.seen)
        self.assertAllFalse(ma.fav, ma.dislike, ma.want, ma.ignore, ma.have)
        ma.seen = False
        self.assertAllFalse(ma.fav, ma.like, ma.seen, ma.dislike, ma.want, ma.ignore, ma.have)
        ma.fav = True
        self.assertAllTrue(ma.seen, ma.like)
        ma.dislike = True
        self.assertAllFalse(ma.fav, ma.like)
        self.assertAllTrue(ma.dislike, ma.seen)

    def test_person_attitude_fields(self):
        ma = PersonRelation()
        self.assertAllFalse(ma.fav, ma.like, ma.dislike)
        ma.fav = True
        self.assertAllTrue(ma.like)
        ma.dislike = True
        self.assertAllFalse(ma.fav, ma.like)
        ma.like = True
        self.assertAllFalse(ma.fav, ma.dislike)
        ma.fav = True
        ma.like = False
        self.assertAllFalse(ma.fav)


class RelationsTest(TestCase):
    def test_delete_empty_relations(self):
        """
        Signal should delete records with False relations
        """
        ma = MovieRelationFactory(seen=True)
        relation_changed.send(sender=MovieRelation, instance=ma, code='seen')

        self.assertEqual(MovieRelation.objects.count(), 1)

        ma.seen = False
        ma.save()
        relation_changed.send(sender=MovieRelation, instance=ma, code=None)

        self.assertEqual(MovieRelation.objects.count(), 0)

    def test_count_of_familiar_objects(self):
        """
        Count of user familiar objects
        """
        ma1 = MovieRelationFactory(seen=True)
        relation_changed.send(sender=MovieRelation, instance=ma1, code='seen')

        count = ma1.user.relations_count
        self.assertEqual(count.movies, 1)

        ma2 = MovieRelationFactory(user=ma1.user, seen=True)
        relation_changed.send(sender=MovieRelation, instance=ma2, code='seen')

        count.refresh_from_db()
        self.assertEqual(count.movies, 2)

        ma1.seen = False
        ma1.save()
        relation_changed.send(sender=MovieRelation, instance=ma1, code=None)

        count.refresh_from_db()
        self.assertEqual(count.movies, 1)

        ma2.seen = False
        ma2.save()
        relation_changed.send(sender=MovieRelation, instance=ma2, code=None)

        count.refresh_from_db()
        self.assertEqual(count.movies, 0)
