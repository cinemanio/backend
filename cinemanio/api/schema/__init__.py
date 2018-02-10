from cinemanio.api.schema.movie import MovieQuery
from cinemanio.api.schema.person import PersonQuery


class Query(MovieQuery, PersonQuery):
    pass
