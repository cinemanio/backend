from vcr_unittest import VCRMixin

from cinemanio.core.factories import MovieFactory, PersonFactory
from cinemanio.core.tests.base import BaseTestCase
from cinemanio.images.models import ImageLink, Image


class ImagesTestCase(VCRMixin, BaseTestCase):
    def test_raise_value_error(self):
        with self.assertRaises(AttributeError):
            ImageLink.objects.get_or_download('')

        with self.assertRaises(AttributeError):
            ImageLink.objects.download('')

    def test_download_kinopoisk_image_for_object(self):
        url = '//st.kp.yandex.net/im/poster/4/8/3/kinopoisk.ru-Les-amants-r_26_23233_3Bguliers-483294.jpg'
        movie = MovieFactory()

        image1, downloaded = movie.images.get_or_download(url, type=Image.POSTER)

        self.assertEqual(downloaded, True)
        self.assertEqual(image1.image.source, 'st.kp.yandex.net')
        self.assertEqual(image1.image.source_type, 'kinopoisk')
        self.assertEqual(image1.image.source_id, '483294')
        self.assertEqual(image1.object, movie)
        self.assertEqual(image1, movie.images.last())

        image2, downloaded = movie.images.get_or_download(url)

        self.assertEqual(downloaded, False)
        self.assertEqual(image1, image2)

    def test_download_wikipedia_image_for_object(self):
        url = 'http://upload.wikimedia.org/wikipedia/commons/9/9e/Francis_Ford_Coppola_2007_crop.jpg'
        person = PersonFactory()

        link = person.images.download(url, type=Image.PHOTO)

        self.assertEqual(link.image.source, 'upload.wikimedia.org')
        self.assertEqual(link.image.source_type, 'wikicommons')
        self.assertEqual(link.image.source_id, 'Francis_Ford_Coppola_2007_crop.jpg')
        self.assertEqual(link.object, person)
        self.assertEqual(link, person.images.last())
