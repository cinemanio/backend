from django_filters import ModelMultipleChoiceFilter
from cinemanio.core.models import Person, Role

from .base import BaseFilterSet


class PersonFilterSet(BaseFilterSet):
    roles = ModelMultipleChoiceFilter(queryset=Role.objects.all(), method='filter_m2m')

    class Meta:
        model = Person
        fields = ['country', 'roles']
