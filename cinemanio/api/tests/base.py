from collections import namedtuple

from cinemanio.core.tests.base import BaseTestCase
from cinemanio.users.factories import UserFactory

Context = namedtuple('Context', ['user'])


class ListQueryBaseTestCase(BaseTestCase):
    def assertCountNonZeroAndEqual(self, result, count):
        self.assertGreater(count, 0)
        self.assertEqual(len(result['edges']), count)


class ObjectQueryBaseTestCase(BaseTestCase):
    def assertM2MRel(self, result, queryset, fieldname='name'):
        self.assertListEqual([r[fieldname] for r in result], list(queryset.values_list('name', flat=True)))


class UserQueryBaseTestCase(BaseTestCase):
    password = 'secret'
    Context = namedtuple('Context', ['user'])

    def create_user(self, **kwargs):
        self.user = UserFactory(username='user', **kwargs)
        self.user.set_password(self.password)
        self.user.save()

    @property
    def context(self):
        return self.Context(user=self.user)
