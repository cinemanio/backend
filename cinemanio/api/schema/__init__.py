from cinemanio.api.schema.movie import MovieQuery
from cinemanio.api.schema.person import PersonQuery
from cinemanio.api.schema.properties import GenreType, LanguageType, CountryType


class Query(MovieQuery, PersonQuery):
    pass
