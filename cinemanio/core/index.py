# from algoliasearch_django import AlgoliaIndex
# from algoliasearch_django.decorators import register
#
# from .models import Movie, Person
#
#
# @register(Movie)
# class MovieIndex(AlgoliaIndex):
#     fields = ('title_en', 'title_ru', 'title_original', 'year')
#     settings = {'searchableAttributes': ['title_en', 'title_ru', 'title_original']}
#     index_name = 'movie'
#     custom_objectID = 'global_id'
#
#
# @register(Person)
# class PersonIndex(AlgoliaIndex):
#     fields = ('name_en', 'name_ru')
#     settings = {'searchableAttributes': ['name_en', 'name_ru']}
#     index_name = 'person'
#     custom_objectID = 'global_id'
