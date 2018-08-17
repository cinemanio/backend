from graphql_relay.node.node import to_global_id
from parameterized import parameterized

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
        query_name = instance.__class__.__name__.lower()
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
            result = self.execute(query, dict(id=to_global_id(node._meta.name, instance.id)))

        self.assertEqual(len(result[query_name]['wikipedia']['edges']), 2)
        self.assertEqual(result[query_name]['wikipedia']['edges'][0]['node']['title'], en.title)
        self.assertEqual(result[query_name]['wikipedia']['edges'][1]['node']['title'], ru.title)
