from cinemanio.api.schema.movie import MovieQuery
from cinemanio.api.schema.person import PersonQuery
from cinemanio.api.schema.properties import GenreType, LanguageType, CountryType  # noqa
from cinemanio.api.schema.imdb_movie import ImdbMovieNode  # noqa
from cinemanio.api.schema.kinopoisk_movie import KinopoiskMovieNode  # noqa


class Query(MovieQuery, PersonQuery):
    pass
