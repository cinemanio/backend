from .auth import AuthTestCase
from .movie import MovieQueryTestCase
from .movies import MoviesQueryTestCase
from .person import PersonQueryTestCase
from .persons import PersonsQueryTestCase
from .properties import PropertiesQueryTestCase
from .relations import RelationsQueryTestCase
from .pagination import PaginationQueryTestCase
from .images import ImagesQueryTestCase
from .wikipedia import WikipediaQueryTestCase

__all__ = [
    'MovieQueryTestCase',
    'MoviesQueryTestCase',
    'PersonQueryTestCase',
    'PersonsQueryTestCase',
    'PropertiesQueryTestCase',
    'AuthTestCase',
    'RelationsQueryTestCase',
    'PaginationQueryTestCase',
    'ImagesQueryTestCase',
    'WikipediaQueryTestCase',
]
