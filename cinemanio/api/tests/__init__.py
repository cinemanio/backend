from .auth import AuthTestCase
from .images import ImagesQueryTestCase
from .movie import MovieQueryTestCase
from .movies import MoviesQueryTestCase
from .pagination import PaginationQueryTestCase
from .person import PersonQueryTestCase
from .persons import PersonsQueryTestCase
from .properties import PropertiesQueryTestCase
from .register import (
    RegisterUserTestCase, ActivateUserTestCase, ResetPasswordRequestTestCase, ResetPasswordTestCase,
    ChangePasswordTestCase, UpdateUserTestCase
)
from .relations import RelationsQueryTestCase
from .search import SearchQueryTestCase
from .wikipedia import WikipediaQueryTestCase


__all__ = [
    'MovieQueryTestCase',
    'MoviesQueryTestCase',
    'PersonQueryTestCase',
    'PersonsQueryTestCase',
    'PropertiesQueryTestCase',
    'RelationsQueryTestCase',
    'PaginationQueryTestCase',
    'ImagesQueryTestCase',
    'WikipediaQueryTestCase',
    'SearchQueryTestCase',
    'AuthTestCase',
    # register
    'RegisterUserTestCase',
    'ActivateUserTestCase',
    'ResetPasswordRequestTestCase',
    'ResetPasswordTestCase',
    'ChangePasswordTestCase',
    'UpdateUserTestCase',
]
