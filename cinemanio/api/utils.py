import graphene
from graphene.utils.str_converters import to_snake_case
from django.db.models.fields.related import ForeignKey
from graphene_django.filter import DjangoFilterConnectionField as _DjangoFilterConnectionField


def getEnum(OldEnum):
    props = {prop.name: prop.value for prop in OldEnum.values.values()}
    return type(OldEnum.__name__, (graphene.Enum,), props)


class DjangoFilterConnectionField(_DjangoFilterConnectionField):
    """
    Temporary fix for select_related issue
    """

    def __init__(self, node):
        super(DjangoFilterConnectionField, self).__init__(node, fields=node._meta.filter_fields)

    @staticmethod
    def merge_querysets(default_queryset, queryset):
        queryset_merged = _DjangoFilterConnectionField.merge_querysets(default_queryset, queryset)
        queryset_merged.query.select_related = queryset.query.select_related
        return queryset_merged


class DjangoObjectTypeMixin:
    """
    Cast select_related to queryset for ForeignKeys of model
    """

    @classmethod
    def get_node(cls, info, id):
        try:
            return cls.get_queryset(info).get(pk=id)
        except cls._meta.model.DoesNotExist:
            return None

    @classmethod
    def get_queryset(cls, info):
        queryset = cls._meta.model.objects.all()
        fields = cls.select_related_fields()

        selections = info.operation.selection_set.selections
        found = False
        while True:
            if found or selections[0].selection_set is None:
                break
            selections = selections[0].selection_set.selections
            if selections[0].name.value in [cls._meta.model._meta.model_name, 'node']:
                found = True

        for field in selections:
            value = to_snake_case(field.name.value)
            if value in fields:
                queryset = queryset.select_related(value)
        return queryset

    @classmethod
    def select_related_fields(cls):
        return [field.name for field in cls._meta.model._meta.fields if isinstance(field, ForeignKey)]
