from django_filters import ModelMultipleChoiceFilter
from cinemanio.core.models import Movie, Genre, Language, Country

from .base import BaseFilterSet


class MovieFilterSet(BaseFilterSet):
    genres = ModelMultipleChoiceFilter(queryset=Genre.objects.all(), method='filter_m2m')
    languages = ModelMultipleChoiceFilter(queryset=Language.objects.all(), method='filter_m2m')
    countries = ModelMultipleChoiceFilter(queryset=Country.objects.all(), method='filter_m2m')

    class Meta:
        model = Movie
        fields = ['year', 'genres', 'languages', 'countries']
