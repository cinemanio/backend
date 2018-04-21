from cinemanio.core.models import Movie, Genre, Language, Country

from .base import BaseFilterSet, ModelGlobalIdMultipleChoiceFilter


class MovieFilterSet(BaseFilterSet):
    genres = ModelGlobalIdMultipleChoiceFilter(queryset=Genre.objects.all(), method='filter_m2m')
    languages = ModelGlobalIdMultipleChoiceFilter(queryset=Language.objects.all(), method='filter_m2m')
    countries = ModelGlobalIdMultipleChoiceFilter(queryset=Country.objects.all(), method='filter_m2m')

    class Meta:
        model = Movie
        fields = ['year', 'genres', 'languages', 'countries']
