from cinemanio.core.factories import MovieFactory, PersonFactory
from cinemanio.core.tests.base import BaseTestCase


class FactoriesTest(BaseTestCase):
    def test_movie(self):
        m = MovieFactory()
        self.assertGreater(len(m.title), 0)
        self.assertIsNotNone(m.year)
        self.assertGreater(m.genres.count(), 0)
        self.assertGreater(m.countries.count(), 0)
        self.assertGreater(m.languages.count(), 0)

    def test_person(self):
        p = PersonFactory()
        self.assertGreater(len(p.first_name), 0)
        self.assertGreater(len(p.last_name), 0)
        self.assertGreater(p.roles.count(), 0)
        self.assertIsNotNone(p.country)
        self.assertIsNotNone(p.date_birth)
        self.assertIsNotNone(p.date_death)
        self.assertIsNotNone(p.gender)
