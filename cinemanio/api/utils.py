import graphene
from graphql.language.ast import FragmentSpread
from django.db.models.fields.related import ForeignKey
from django.db.models.fields.reverse_related import OneToOneRel
from graphene.utils.str_converters import to_snake_case
from graphene_django.filter import DjangoFilterConnectionField as _DjangoFilterConnectionField


class DjangoFilterConnectionField(_DjangoFilterConnectionField):
    """
    Temporary fix for select_related issue
    """

    def __init__(self, node, **kwargs):
        super(DjangoFilterConnectionField, self).__init__(node, fields=node._meta.filter_fields, **kwargs)

    @classmethod
    def merge_querysets(cls, default_queryset, queryset):
        if default_queryset.query.distinct != queryset.query.distinct:
            queryset_merged = default_queryset
        else:
            queryset_merged = _DjangoFilterConnectionField.merge_querysets(default_queryset, queryset)
        queryset_merged.query.select_related = queryset.query.select_related
        # pylint: disable=protected-access
        queryset_merged._prefetch_related_lookups = queryset._prefetch_related_lookups
        return queryset_merged


class DjangoObjectTypeMixin:
    """
    Cast select_related to queryset for ForeignKeys of model
    """

    @classmethod
    def get_node(cls, info, pk):
        try:
            return cls.get_queryset(info).get(pk=pk)
        except cls._meta.model.DoesNotExist:
            return None

    @classmethod
    def get_queryset(cls, info):
        queryset = cls._meta.model.objects.all()
        fields = cls.select_foreign_keys() + cls.select_o2o_related_objects()
        fields_m2m = cls.select_m2m_fields()
        selections = cls.get_selections(info)
        fields_to_select = cls.convert_selections_to_fields(selections, info)

        for field_to_select in fields_to_select:
            field_to_select = to_snake_case(field_to_select)
            if field_to_select in fields:
                queryset = queryset.select_related(field_to_select)
            if field_to_select in fields_m2m:
                queryset = queryset.prefetch_related(field_to_select)

        return queryset

    @classmethod
    def convert_selections_to_fields(cls, selections, info):
        fields = []
        for selection in selections:
            if isinstance(selection, FragmentSpread):
                fields += cls.convert_selections_to_fields(
                    info.fragments[selection.name.value].selection_set.selections, info)
            else:
                fields.append(selection.name.value)
        return fields

    @classmethod
    def get_selections(cls, info):
        selections = [info.field_asts[0]]
        found = False
        i = 0
        while True:
            if selections[i].selection_set is None:
                if i >= len(selections):
                    break
                else:
                    i += 1
                    continue

            if selections[i].name.value in [cls._meta.model._meta.model_name, 'node']:
                found = True

            selections = selections[i].selection_set.selections
            i = 0

            if found is True and selections[0].name.value == 'edges':
                found = False

            if found:
                break

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


class CountableConnectionBase(graphene.relay.Connection):
    class Meta:
        abstract = True

    total_count = graphene.Int()

    def resolve_total_count(self, _):
        return self.iterable.count()
