from cinemanio.schema import schema


def execute(query):
    result = schema.execute(query)
    assert not result.errors, result.errors
    return result.data
