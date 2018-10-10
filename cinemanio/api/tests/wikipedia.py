from parameterized import parameterized

from cinemanio.api.helpers import global_id
from cinemanio.api.schema.movie import MovieNode
from cinemanio.api.schema.person import PersonNode
from cinemanio.api.tests.base import QueryBaseTestCase
from cinemanio.core.factories import MovieFactory, PersonFactory
from cinemanio.sites.wikipedia.factories import WikipediaPageFactory


class WikipediaQueryTestCase(QueryBaseTestCase):
    @parameterized.expand([
        (MovieFactory, MovieNode),
        (PersonFactory, PersonNode),
    ])
    def test_object_wikipedia_pages(self, factory, node):
        instance = factory()
        en = WikipediaPageFactory(content_object=instance, lang='en')
        ru = WikipediaPageFactory(content_object=instance, lang='ru')
        query_name = instance._meta.model_name
        query = '''
            query Movie($id: ID!) {
              %s(id: $id) {
                id
                wikipedia {
                  edges {
                    node {
                      title
                      lang
                      content
                    }
                  }
                }
              }
            }
        ''' % query_name

        with self.assertNumQueries(3):
            result = self.execute(query, dict(id=global_id(instance)))

        self.assertEqual(len(result[query_name]['wikipedia']['edges']), 2)
        self.assertEqual(result[query_name]['wikipedia']['edges'][0]['node']['title'], en.title)
        self.assertEqual(result[query_name]['wikipedia']['edges'][1]['node']['title'], ru.title)
