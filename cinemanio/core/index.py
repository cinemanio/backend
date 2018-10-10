from algoliasearch_django import AlgoliaIndex
from algoliasearch_django.decorators import register

from .models import Movie, Person


@register(Movie)
class MovieIndex(AlgoliaIndex):
    fields = ('title_en', 'title_ru', 'title_original', 'year')
    settings = {'searchableAttributes': ['title_en', 'title_ru', 'title_original']}
    index_name = 'movie'


@register(Person)
class PersonIndex(AlgoliaIndex):
    fields = ('first_name_en', 'last_name_en', 'first_name_ru', 'last_name_ru')
    settings = {'searchableAttributes': ['first_name_en', 'last_name_en', 'first_name_ru', 'last_name_ru']}
    index_name = 'person'
