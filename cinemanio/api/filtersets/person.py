from django_filters import ChoiceFilter, OrderingFilter

from cinemanio.core.models import Person, Role
from cinemanio.relations.models import PersonRelation

from .base import BaseFilterSet, ModelGlobalIdMultipleChoiceFilter
from .relations import RelationsMixin, get_relations_ordering_fields

codes = PersonRelation().codes


class PersonFilterSet(BaseFilterSet, RelationsMixin):
    roles = ModelGlobalIdMultipleChoiceFilter(queryset=Role.objects.all(), method='filter_m2m')
    relation = ChoiceFilter(choices=[[code] * 2 for code in codes], method='filter_relation')
    order_by = OrderingFilter(fields=get_relations_ordering_fields(codes))

    class Meta:
        model = Person
        fields = ['country', 'roles', 'relation']
