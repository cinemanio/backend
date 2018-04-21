from graphql_relay.node.node import from_global_id
from django_filters import FilterSet
from django_filters.filters import ModelMultipleChoiceFilter, ModelMultipleChoiceField


class BaseFilterSet(FilterSet):
    def filter_m2m(self, qs, name, value):
        for instance in value:
            qs = qs.filter(**{name: instance.id})
        return qs


class ModelGlobalIdMultipleChoiceField(ModelMultipleChoiceField):
    """
    Multiple choice field with support of relay global_id
    """
    def _check_values(self, value):
        # TODO: check type of global id
        value = [int(from_global_id(global_id)[1]) for global_id in value]
        return super()._check_values(value)


class ModelGlobalIdMultipleChoiceFilter(ModelMultipleChoiceFilter):
    """
    Multiple choice filter with support of relay global_id
    """
    field_class = ModelGlobalIdMultipleChoiceField
