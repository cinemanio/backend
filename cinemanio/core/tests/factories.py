from cinemanio.core.factories import MovieFactory
from cinemanio.core.tests.base import BaseTestCase


class FactoriesTest(BaseTestCase):
    def test_movie(self):
        m = MovieFactory()
        self.assertGreater(len(m.title), 0)
        self.assertIsNotNone(m.year)
        self.assertGreater(m.genres.count(), 0)
        self.assertGreater(m.countries.count(), 0)
        self.assertGreater(m.languages.count(), 0)
