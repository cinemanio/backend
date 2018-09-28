from typing import Type
from django.contrib import admin

from .movie import MovieAdmin
from .person import PersonAdmin
from .properties import GenreAdmin, LanguageAdmin, CountryAdmin

__all__ = [
    'MovieAdmin',
    'PersonAdmin',
    'GenreAdmin',
    'LanguageAdmin',
    'CountryAdmin',
    'get_registered_admin_class',
]


def get_registered_admin_class(model) -> Type[admin.ModelAdmin]:
    return admin.site._registry[model].__class__  # pylint: disable=protected-access
