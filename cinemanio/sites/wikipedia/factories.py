import random
import factory
from factory.django import DjangoModelFactory
from django.conf import settings

from cinemanio.sites.wikipedia.models import WikipediaPage


class WikipediaPageFactory(DjangoModelFactory):
    title = factory.Faker('sentence', nb_words=3)
    lang = factory.LazyAttribute(lambda o: random.choice([lang[0] for lang in settings.LANGUAGES]))
    content = factory.Faker('text')

    class Meta:
        model = WikipediaPage
