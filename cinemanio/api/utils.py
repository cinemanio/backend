import graphene
from django.db.models.fields.related import ForeignKey
from django.db.models.fields.reverse_related import OneToOneRel
from graphene.utils.str_converters import to_snake_case
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
        if default_queryset.query.distinct != queryset.query.distinct:
            queryset_merged = default_queryset
        else:
            queryset_merged = _DjangoFilterConnectionField.merge_querysets(default_queryset, queryset)
        queryset_merged.query.select_related = queryset.query.select_related
        queryset_merged._prefetch_related_lookups = queryset._prefetch_related_lookups
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
        fields = cls.select_foreign_keys() + cls.select_o2o_related_objects()
        fields_m2m = cls.select_m2m_fields()
        selections = cls.get_selections(info)

        for field in selections:
            value = to_snake_case(field.name.value)
            if value in fields:
                queryset = queryset.select_related(value)
            if value in fields_m2m:
                queryset = queryset.prefetch_related(value)

        return queryset

    @classmethod
    def get_selections(cls, info):
        selections = info.operation.selection_set.selections
        found = False
        while True:
            if selections[0].selection_set is None or found:
                break
            if selections[0].name.value in [cls._meta.model._meta.model_name, 'node']:
                found = True
            selections = selections[0].selection_set.selections
        return selections

    @classmethod
    def select_foreign_keys(cls):
        return [field.name for field in cls._meta.model._meta.fields if isinstance(field, ForeignKey)]

    @classmethod
    def select_m2m_fields(cls):
        return [field.name for field in cls._meta.model._meta.many_to_many]

    @classmethod
    def select_o2o_related_objects(cls):
        return [rel.related_name for rel in cls._meta.model._meta.related_objects if isinstance(rel, OneToOneRel)]
