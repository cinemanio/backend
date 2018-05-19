from cinemanio.api.schema.movie import MovieQuery
from cinemanio.api.schema.person import PersonQuery
from cinemanio.api.schema.properties import PropertiesQuery, GenreNode, LanguageNode, CountryNode, RoleNode  # noqa
from cinemanio.api.schema.cast import CastNode  # noqa
from cinemanio.api.schema.image import ImageNode, ImageLinkNode  # noqa
from cinemanio.api.schema.imdb import ImdbMovieNode, ImdbPersonNode  # noqa
from cinemanio.api.schema.kinopoisk import KinopoiskMovieNode, KinopoiskPersonNode  # noqa


class Query(MovieQuery, PersonQuery, PropertiesQuery):
    pass
