import graphene

from cinemanio.api import schema


class Query(schema.Query, graphene.ObjectType):
    """
    This class will inherit from multiple Queries as we begin to add more apps to our project
    """


schema = graphene.Schema(query=Query)
