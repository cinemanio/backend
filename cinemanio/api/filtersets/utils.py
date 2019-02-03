from django.db.models import F
from django_filters import OrderingFilter


class OrderingWithNullsFilter(OrderingFilter):

    def get_ordering_value(self, param):
        descending = param.startswith('-')
        param = param[1:] if descending else param
        field_name = self.param_map.get(param, param)

        if descending:
            return F(field_name).desc(nulls_last=True)
        else:
            return F(field_name).asc(nulls_first=True)
