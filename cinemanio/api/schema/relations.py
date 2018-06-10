import graphene
from graphql_relay.node.node import from_global_id
from graphene_django import DjangoObjectType
from django.db.transaction import atomic

from cinemanio.relations.models import MovieRelation, PersonRelation, MovieRelationCount, PersonRelationCount
from cinemanio.relations.signals import relation_changed

EXCLUDE_FIELDS = ('object', 'user')


class MovieRelationNode(DjangoObjectType):
    class Meta:
        model = MovieRelation
        exclude_fields = EXCLUDE_FIELDS


class PersonRelationNode(DjangoObjectType):
    class Meta:
        model = PersonRelation
        exclude_fields = EXCLUDE_FIELDS


class MovieRelationCountNode(DjangoObjectType):
    class Meta:
        model = MovieRelationCount
        exclude_fields = EXCLUDE_FIELDS


class PersonRelationCountNode(DjangoObjectType):
    class Meta:
        model = PersonRelationCount
        exclude_fields = EXCLUDE_FIELDS


class RelationNode(graphene.Union):
    class Meta:
        types = (MovieRelationNode, PersonRelationNode)


class RelationCountNode(graphene.Union):
    class Meta:
        types = (MovieRelationCountNode, PersonRelationCountNode)


class Relate(graphene.Mutation):
    class Arguments:
        id = graphene.ID()
        type = graphene.String()

    count = graphene.Field(RelationCountNode)
    relation = graphene.Field(RelationNode)

    models_map = {
        'MovieNode': MovieRelation,
        'PersonNode': PersonRelation,
    }

    def mutate(self, info, id, type):
        user = info.context.user
        node_name, instance_id = from_global_id(id)

        with atomic():
            try:
                relation = Relate.models_map[node_name].objects.get_or_create(object_id=instance_id, user=user)[0]
            except KeyError:
                raise ValueError(f"Unrecognized node {id}")
            relation.change(type)
            relation.save()
            relation_changed.send(sender=relation.__class__, instance=relation)

        return Relate(
            count=relation.object.relations_count,
            relation=relation,
        )


class RelationMutation:
    relate = Relate.Field()
