from cinemanio.core.tests.base import BaseTestCase
from cinemanio.core.utils.languages import translated_fields


class LanguagesTest(BaseTestCase):
    def test_translated_fields_one(self):
        self.assertEqual(translated_fields('field'), ['field_en', 'field_ru'])

    def test_translated_fields_with_base(self):
        self.assertEqual(translated_fields('field', with_base=True), ['field', 'field_en', 'field_ru'])

    def test_translated_fields_multiple(self):
        self.assertEqual(translated_fields('field1', 'field2'), ['field1_en', 'field2_en', 'field1_ru', 'field2_ru'])
