from cinemanio.schema import schema


def execute(query, values=None):
    result = schema.execute(query, variable_values=values)
    assert not result.errors, result.errors
    return result.data
