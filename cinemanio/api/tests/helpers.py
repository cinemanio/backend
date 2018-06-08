from cinemanio.schema import schema


def execute(query, values=None, context=None):
    result = schema.execute(query, variable_values=values, context_value=context)
    assert not result.errors, result.errors
    return result.data
