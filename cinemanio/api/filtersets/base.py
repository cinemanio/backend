# from graphql_relay.node.node import from_global_id
from django_filters import FilterSet


class BaseFilterSet(FilterSet):
    def filter_m2m(self, qs, name, value):
        # TODO: switch to use global ids
        for instance in value:
            qs = qs.filter(**{name: instance.id})
        return qs
