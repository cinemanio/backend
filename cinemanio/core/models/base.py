from typing import Iterable
from algoliasearch_django import raw_search
from django.db import models
from django.db.models import QuerySet
from django.utils.translation import ugettext_lazy as _
from transliterate import translit
from transliterate.base import registry

from cinemanio.core.translit.ru import RussianLanguagePack
from cinemanio.api.helpers import global_id

registry.register(RussianLanguagePack)


class BaseModel(models.Model):
    """
    Base model for Movie and Person
    """
    # TODO: remove field
    slug = models.SlugField(_('Slug'), max_length=100, unique=True, null=True, blank=True)

    site_official_url = models.URLField(_('Official site'), null=True, blank=True)
    site_fan_url = models.URLField(_('Fan site'), null=True, blank=True)

    class Meta:
        abstract = True

    def __str__(self):
        return repr(self)

    @property
    def global_id(self):
        return global_id(self)

    @property
    def transliteratable_fields(self):
        raise NotImplementedError()

    def set_transliteratable_fields(self):
        """
        If some fields non-specified in English, but specified in other language -
        assign transliteratable version for the English and main field
        """
        for lang in ['ru']:
            for field in self.transliteratable_fields:
                field_lang = '{}_{}'.format(field, lang)
                field_en = '{}_{}'.format(field, 'en')
                value_lang = getattr(self, field_lang)
                value_en = getattr(self, field_en)
                value = getattr(self, field)
                if value_lang:
                    if not value or not value_en:
                        value_translit = translit(value_lang, lang, reversed=True)
                        if not value:
                            setattr(self, field, value_translit)
                        if not value_en:
                            setattr(self, field_en, value_translit)


class BaseQuerySet(models.QuerySet):
    """
    Base queryset for Movie and Person
    """
    search_result_ids = []

    def search(self, term: str) -> 'QuerySet':
        """
        Search by term using algolia search engine, filter results using ids from DB
        :param term: search term
        :return:
        """
        params = {"hitsPerPage": 100}
        response = raw_search(self.model, term, params)
        self.search_result_ids = [hit['objectID'] for hit in response['hits']]
        return self.filter(id__in=self.search_result_ids)

    def _chain(self, **kwargs) -> 'QuerySet':
        """
        Preserve search results order from old queryset to new
        """
        obj = super()._chain(**kwargs)
        obj.search_result_ids = self.search_result_ids
        return obj

    def order_by(self, *field_names):
        """
        Flush search results order, when another order provided
        """
        obj = super().order_by(*field_names)
        obj.search_result_ids = []
        return obj

    @property
    def ordered(self) -> bool:
        """
        Return True if search results defined or use regular Django logic
        """
        return self.search_result_ids or super().ordered

    def __iter__(self) -> Iterable:
        """
        Sort results using search results order if it's defined
        """
        self._fetch_all()
        if self.search_result_ids:
            self._result_cache = sorted(self._result_cache, key=self.search_sort_helper)
        return iter(self._result_cache)

    def search_sort_helper(self, i):
        return self.search_result_ids.index(i.id if isinstance(i, models.Model) else i)
