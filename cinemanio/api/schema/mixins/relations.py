import graphene
from django.core.exceptions import ObjectDoesNotExist
from cinemanio.api.schema.relations import RelationNode, RelationCountNode


class RelationsMixin:
    relation = graphene.Field(RelationNode)
    relations_count = graphene.Field(RelationCountNode)

    def resolve_relation(self, info, *args, **kwargs):
        user = info.context.user
        if not user or not user.is_authenticated:
            return None

        try:
            return self.relations.get(user=user)
        except ObjectDoesNotExist:
            return self.relations.field.model(object=self, user=user)

    def resolve_relations_count(self, info, *args, **kwargs):
        try:
            return self.relations_count
        except ObjectDoesNotExist:
            return self._meta.get_field('relations_count').related_model()
