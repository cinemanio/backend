from django_filters import ChoiceFilter, OrderingFilter

from cinemanio.core.models import Movie, Genre, Language, Country
from cinemanio.relations.models import MovieRelation

from .base import BaseFilterSet, ModelGlobalIdMultipleChoiceFilter
from .relations import RelationsMixin, get_relations_ordering_fields

codes = MovieRelation().codes


class MovieFilterSet(BaseFilterSet, RelationsMixin):
    genres = ModelGlobalIdMultipleChoiceFilter(queryset=Genre.objects.all(), method='filter_m2m')
    languages = ModelGlobalIdMultipleChoiceFilter(queryset=Language.objects.all(), method='filter_m2m')
    countries = ModelGlobalIdMultipleChoiceFilter(queryset=Country.objects.all(), method='filter_m2m')
    relation = ChoiceFilter(choices=[[code] * 2 for code in codes], method='filter_relation')
    order_by = OrderingFilter(fields=[('year', 'year')] + get_relations_ordering_fields(codes))

    class Meta:
        model = Movie
        fields = ['year', 'genres', 'languages', 'countries', 'relation']
