from typing import Tuple, Generator
from django.conf import settings


def iter_languages() -> Generator:
    for lang, _ in settings.LANGUAGES:
        yield lang


def translated_fields(*args, with_base=False) -> Tuple[str, ...]:
    fields = [f'{field_name}_{lang}' for lang in iter_languages() for field_name in args]
    if with_base:
        fields = list(args) + fields
    return tuple(fields)
