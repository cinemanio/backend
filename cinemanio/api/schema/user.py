import graphene
from django.contrib.auth import get_user_model
from graphene import relay
from graphene_django import DjangoObjectType
from graphql_jwt.decorators import login_required

User = get_user_model()


class UserNode(DjangoObjectType):
    class Meta:
        model = User
        interfaces = (relay.Node,)
        only_fields = ('email', 'username', 'first_name', 'last_name',)


class UserQuery:
    me = graphene.Field(UserNode)

    @login_required
    def resolve_me(self, info):
        if info.context.user.is_authenticated:
            return UserNode.get_node(info, info.context.user.id)
        return None
