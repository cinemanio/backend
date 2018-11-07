from parameterized import parameterized

from cinemanio.api.helpers import global_id
from cinemanio.api.schema.movie import MovieNode
from cinemanio.api.schema.person import PersonNode
from cinemanio.api.tests.base import QueryBaseTestCase
from cinemanio.core.factories import MovieFactory, PersonFactory
from cinemanio.images.factories import ImageLinkFactory
from cinemanio.images.models import ImageType


class ImagesQueryTestCase(QueryBaseTestCase):
    @parameterized.expand([
        (MovieFactory, MovieNode, ImageType.POSTER),
        (PersonFactory, PersonNode, ImageType.PHOTO),
    ])
    def test_object_images(self, factory, node, image_type):
        instance = factory()
        for i in range(10):
            ImageLinkFactory(object=instance, image__type=image_type)
        query_name = instance._meta.model_name
        query = '''
            query Object($id: ID!) {
              %s(id: $id) {
                id
                images {
                  edges {
                    node {
                      image {
                        type
                        original
                        fullCard
                        shortCard
                        detail
                        icon
                      }
                    }
                  }
                }
              }
            }
        ''' % query_name
        # TODO: reduce number of queries
        with self.assertNumQueries(3 + (4 * 10)):
            result = self.execute(query, dict(id=global_id(instance)))
        self.assertEqual(len(result[query_name]['images']['edges']), instance.images.count())
        first = result[query_name]['images']['edges'][0]['node']['image']
        self.assertEqual(first['type'], image_type.name)
        self.assertTrue(len(first['original']) > 0)
        self.assertTrue(len(first['icon']) > 0)

    @parameterized.expand([
        (MovieFactory, MovieNode, ImageType.POSTER, 'poster'),
        (PersonFactory, PersonNode, ImageType.PHOTO, 'photo'),
    ])
    def test_object_image(self, factory, node, image_type, field):
        instance = factory()
        query_name = instance._meta.model_name
        query = '''
            query Object($id: ID!) {
              %s(id: $id) {
                id
                %s {
                  type
                  original
                  fullCard
                  shortCard
                  detail
                  icon
                }
              }
            }
        ''' % (query_name, field)
        values = dict(id=global_id(instance))

        # no images
        with self.assertNumQueries(3):
            result_nothing = self.execute(query, values)
        self.assertEqual(result_nothing[query_name][field], None)

        # images
        for i in range(100):
            ImageLinkFactory(object=instance, image__type=image_type)

        with self.assertNumQueries(3 + 4):
            result = self.execute(query, values)
        self.assertEqual(result[query_name][field]['type'], image_type.name)
        self.assertTrue(len(result[query_name][field]['original']) > 0)

        # try again to check random image
        result_another = self.execute(query, values)
        self.assertNotEqual(result[query_name][field]['original'], result_another[query_name][field]['original'])
