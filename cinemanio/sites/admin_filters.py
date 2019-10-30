from django.contrib import admin
from django.utils.translation import gettext_lazy as _


class BaseFilter(admin.SimpleListFilter):
    def lookups(self, request, model_admin):
        return (
            ('present', _('with link')),
            ('no', _('no link')),
            ('uptodate', _('up to date')),
            ('outdated', _('outdated')),
        )

    def queryset(self, request, queryset):
        if self.value() == 'present':
            return queryset.with_site(self.parameter_name)
        if self.value() == 'no':
            return queryset.without_site(self.parameter_name)
        if self.value() == 'uptodate':
            return queryset.with_site_uptodate(self.parameter_name)
        if self.value() == 'outdated':
            return queryset.with_site_outdated(self.parameter_name)


class ImdbFilter(BaseFilter):
    title = _('IMDb')
    parameter_name = 'imdb'


class KinopoiskFilter(BaseFilter):
    title = _('Kinopoisk')
    parameter_name = 'kinopoisk'


def get_wikipedia_filter(lang):
    class WikipediaFilter(BaseFilter):
        title = _(f'Wikipedia {lang.upper()}')
        parameter_name = f'wikipedia_{lang}'

        def queryset(self, request, queryset):
            if self.value() == 'present':
                return queryset.with_site('wikipedia', lang)
            if self.value() == 'no':
                return queryset.without_site('wikipedia', lang)
            if self.value() == 'uptodate':
                return queryset.with_site_uptodate('wikipedia', lang)
            if self.value() == 'outdated':
                return queryset.with_site_outdated('wikipedia', lang)
    return WikipediaFilter


wikipedia_filters = tuple([get_wikipedia_filter(lang) for lang in ['en', 'ru']])
