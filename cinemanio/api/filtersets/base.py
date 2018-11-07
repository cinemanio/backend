from graphql_relay.node.node import from_global_id
from django_filters import FilterSet, CharFilter
from django_filters.filters import ModelMultipleChoiceFilter, ModelMultipleChoiceField


class BaseFilterSet(FilterSet):
    """
    Base filter set for Movie and Person
    """
    search = CharFilter(method='filter_by_search_term')

    def filter_m2m(self, qs, name, value):
        for instance in value:
            qs = qs.filter(**{name: instance.id})
        return qs

    def filter_by_search_term(self, qs, _, value):
        return qs.search(value)


class ModelGlobalIdMultipleChoiceField(ModelMultipleChoiceField):
    """
    Multiple choice field with support of relay global_id
    """

    def _check_values(self, value):
        from cinemanio.api import schema
        local_ids = []
        for global_id in value:
            node, local_id = from_global_id(global_id)
            node = getattr(schema, node)
            if node._meta.model != self.queryset.model:
                raise ValueError(f"Wrong type of argument value {global_id}")
            local_ids.append(int(local_id))
        return super()._check_values(local_ids)


class ModelGlobalIdMultipleChoiceFilter(ModelMultipleChoiceFilter):
    """
    Multiple choice filter with support of relay global_id
    """
    field_class = ModelGlobalIdMultipleChoiceField
