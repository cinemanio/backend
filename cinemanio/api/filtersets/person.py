from cinemanio.core.models import Person, Role

from .base import BaseFilterSet, ModelGlobalIdMultipleChoiceFilter


class PersonFilterSet(BaseFilterSet):
    roles = ModelGlobalIdMultipleChoiceFilter(queryset=Role.objects.all(), method='filter_m2m')

    class Meta:
        model = Person
        fields = ['country', 'roles']
