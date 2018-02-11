import graphene


class DjangoPrimaryKey(graphene.Interface):
    pk = graphene.ID(description="Primary key")

    def resolve_pk(self, args, context, info):
        return self.pk

