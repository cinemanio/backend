from graphql_relay.node.node import to_global_id


def global_id(instance):
    return to_global_id(f'{instance._meta.object_name}Node', instance.pk)
