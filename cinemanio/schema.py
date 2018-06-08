import graphene
import graphql_jwt

from cinemanio.api import schema


class Mutation(graphene.ObjectType):
    token_auth = graphql_jwt.ObtainJSONWebToken.Field()
    verify_token = graphql_jwt.Verify.Field()
    refresh_token = graphql_jwt.Refresh.Field()


class Query(schema.Query, graphene.ObjectType):
    """
    This class will inherit from multiple Queries as we begin to add more apps to our project
    """


schema = graphene.Schema(query=Query, mutation=Mutation)
