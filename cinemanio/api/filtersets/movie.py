# from graphql_relay.node.node import from_global_id
from django_filters import FilterSet, ModelMultipleChoiceFilter
from cinemanio.core.models import Movie, Genre, Language, Country


class MovieFilterSet(FilterSet):
    genres = ModelMultipleChoiceFilter(queryset=Genre.objects.all(), method='filter_m2m')
    languages = ModelMultipleChoiceFilter(queryset=Language.objects.all(), method='filter_m2m')
    countries = ModelMultipleChoiceFilter(queryset=Country.objects.all(), method='filter_m2m')

    def filter_m2m(self, qs, name, value):
        # TODO: switch to use global ids
        for instance in value:
            qs = qs.filter(**{name: instance.id})
        return qs

    class Meta:
        model = Movie
        fields = ['year', 'genres', 'languages', 'countries']
