from parameterized import parameterized
from unittest import mock

from cinemanio.core.factories import MovieFactory, PersonFactory
from cinemanio.core.models import Movie, Person
from cinemanio.core.tests.base import BaseTestCase


class SearchTest(BaseTestCase):
    def assert_queryset(self, search, indexes):
        return self.assertListEqual(list(search.values_list('id', flat=True)), [self.instances[i].id for i in indexes])

    @parameterized.expand([
        (Movie, MovieFactory),
        (Person, PersonFactory),
    ])
    @mock.patch('cinemanio.core.models.base.raw_search')
    def test_search_preserve_order(self, model, factory, raw_search):
        self.instances = []
        for i in range(100):
            self.instances.append(factory())

        raw_search.return_value = {'hits': [
            {'objectID': self.instances[2].id},
            {'objectID': self.instances[1].id},
            {'objectID': self.instances[0].id},
        ]}

        # check search results order
        with self.assertNumQueries(1):
            search = model.objects.search('')
            self.assert_queryset(search, [2, 1, 0])

        # check regular queryset order
        with self.assertNumQueries(1):
            search = model.objects.search('').order_by('id')
            self.assert_queryset(search, [0, 1, 2])

        # check search results order with filtering
        with self.assertNumQueries(1):
            search = model.objects.filter(id__in=[self.instances[0].id, self.instances[2].id]).search('')
            self.assert_queryset(search, [2, 0])
