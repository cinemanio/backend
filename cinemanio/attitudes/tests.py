from django.contrib.auth import get_user_model
from django.test import TestCase

from cinemanio.attitudes.models import MovieAttitude, PersonAttitude
from cinemanio.core.factories import MovieFactory
from cinemanio.attitudes.factories import MovieAttitudeFactory
from cinemanio.attitudes.signals import attitude_changed

User = get_user_model()


class AttitudesFieldsTest(TestCase):
    def assertAllTrue(self, *args):
        for arg in args:
            self.assertTrue(arg)

    def assertAllFalse(self, *args):
        for arg in args:
            self.assertFalse(arg)

    def test_movie_attitude_fields(self):
        ma = MovieAttitude()
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
        ma = PersonAttitude()
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


class AttitudesTest(TestCase):
    def test_delete_empty_attitudes(self):
        """
        Signal should delete records with False attitudes
        """
        ma = MovieAttitudeFactory(seen=True)
        attitude_changed.send(sender=MovieAttitude, instance=ma, code='seen')

        self.assertEqual(MovieAttitude.objects.count(), 1)

        ma.seen = False
        ma.save()
        attitude_changed.send(sender=MovieAttitude, instance=ma, code=None)

        self.assertEqual(MovieAttitude.objects.count(), 0)

    def test_count_of_familiar_objects(self):
        """
        Count of user familiar objects
        """
        ma1 = MovieAttitudeFactory(seen=True)
        attitude_changed.send(sender=MovieAttitude, instance=ma1, code='seen')

        count = ma1.user.attitudes_count
        self.assertEqual(count.movies, 1)

        ma2 = MovieAttitudeFactory(user=ma1.user, seen=True)
        attitude_changed.send(sender=MovieAttitude, instance=ma2, code='seen')

        count.refresh_from_db()
        self.assertEqual(count.movies, 2)

        ma1.seen = False
        ma1.save()
        attitude_changed.send(sender=MovieAttitude, instance=ma1, code=None)

        count.refresh_from_db()
        self.assertEqual(count.movies, 1)

        ma2.seen = False
        ma2.save()
        attitude_changed.send(sender=MovieAttitude, instance=ma2, code=None)

        count.refresh_from_db()
        self.assertEqual(count.movies, 0)
