import graphene
from graphql_relay.node.node import from_global_id

from cinemanio.core.models import Movie, Person


class Relate(graphene.Mutation):
    class Arguments:
        id = graphene.ID()
        type = graphene.String()

    ok = graphene.Boolean()

    # person = graphene.Field(lambda: Person)

    models_map = {
        'MovieNode': Movie,
        'PersonNode': Person,
    }

    def mutate(self, info, id, type):
        user = info.context.user
        _type, instance_id = from_global_id(id)
        try:
            instance = Relate.models_map[_type].objects.get(id=instance_id)
        except KeyError:
            raise ValueError(f"Unrecognized node {id}")

        relation = instance.relations.get_or_create(user=user)[0]
        relation.change(type)
        relation.save()

        # person = Person(name=name)
        ok = True
        return Relate(
            # person=person,
            ok=ok
        )


class RelationMutation:
    relate = Relate.Field()
