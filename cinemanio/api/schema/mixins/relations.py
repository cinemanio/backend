import graphene
from django.core.exceptions import ObjectDoesNotExist
from django.db.models.query import Prefetch

from cinemanio.api.schema.relations import RelationNode, RelationCountNode


class RelationsMixin:
    relation = graphene.Field(RelationNode)
    relations_count = graphene.Field(RelationCountNode)

    def resolve_relation(self, info, **_):
        user = info.context.user
        empty = self.relations.field.model()

        if not user or not user.is_authenticated:
            return empty

        try:
            return self.user_relation_prefetched[0]
        except (AttributeError, IndexError):
            return empty

    def resolve_relations_count(self, _, **__):
        try:
            return self.relations_count
        except ObjectDoesNotExist:
            return self._meta.get_field('relations_count').related_model()

    @classmethod
    def get_queryset(cls, info, *args, **kwargs):
        user = info.context.user
        queryset = super().get_queryset(info, *args, **kwargs)

        if not user or not user.is_authenticated:
            return queryset

        selections = cls.get_selections(info)
        fields_to_select = cls.convert_selections_to_fields(selections, info)

        for field_to_select in fields_to_select:
            if field_to_select == 'relation':
                model = cls._meta.model._meta.get_field('relations').related_model
                queryset = queryset.prefetch_related(Prefetch(
                    'relations', to_attr='user_relation_prefetched',
                    queryset=model.objects.filter(user_id=user.id)))

        return queryset
