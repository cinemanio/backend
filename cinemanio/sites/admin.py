from django.contrib import admin
from django.contrib.admin import register, TabularInline
from django.contrib.contenttypes.admin import GenericTabularInline
from django.db.models import Prefetch
from django.utils.html import strip_tags, format_html

from cinemanio.core.admin.site import site
from cinemanio.core.admin import get_registered_admin_class
from cinemanio.core.models import Movie, Person
from cinemanio.sites.imdb.models import ImdbMovie, ImdbPerson
from cinemanio.sites.kinopoisk.models import KinopoiskMovie, KinopoiskPerson
from cinemanio.sites.wikipedia.models import WikipediaPage
from cinemanio.sites.admin_filters import ImdbFilter, KinopoiskFilter, wikipedia_filters

MovieAdmin = get_registered_admin_class(Movie)
PersonAdmin = get_registered_admin_class(Person)
admin.site.unregister(Movie)
admin.site.unregister(Person)

LINK = '<a href="{}" target="_blank" title="Open remote link in a new tab">{}</a>'


class InlineMixin:
    classes = ('collapse', 'collapsed',)


class ImdbMovieInline(InlineMixin, TabularInline):
    model = ImdbMovie


class KinopoiskMovieInline(InlineMixin, TabularInline):
    model = KinopoiskMovie


class ImdbPersonInline(InlineMixin, TabularInline):
    model = ImdbPerson


class KinopoiskPersonInline(InlineMixin, TabularInline):
    model = KinopoiskPerson


class WikipediaPageInline(InlineMixin, GenericTabularInline):
    model = WikipediaPage
    extra = 0


class SitesAdminMixin:
    def imdb_id(self, obj):
        return format_html(LINK, obj.imdb.url, obj.imdb.id)

    def kinopoisk_id(self, obj):
        return format_html(LINK, obj.kinopoisk.url, obj.kinopoisk.id)

    def wikipedia_en(self, obj):
        return self.wikipedia(obj, 'en')

    def wikipedia_ru(self, obj):
        return self.wikipedia(obj, 'ru')

    def wikipedia(self, obj, lang):
        try:
            wikipedia = getattr(obj, f'wikipedia_{lang}')[0]
            return format_html(LINK, wikipedia.url, strip_tags(wikipedia.title))
        except IndexError:
            return ''

    def get_queryset(self, request):
        return super().get_queryset(request) \
            .prefetch_related(
            Prefetch('wikipedia', to_attr='wikipedia_en', queryset=WikipediaPage.objects.filter(lang='en'))) \
            .prefetch_related(
            Prefetch('wikipedia', to_attr='wikipedia_ru', queryset=WikipediaPage.objects.filter(lang='ru')))


@register(Movie, site=site)
class SitesMovieAdmin(SitesAdminMixin, MovieAdmin):  # type: ignore
    list_display = MovieAdmin.list_display + ['imdb_id', 'imdb_rating', 'kinopoisk_id', 'kinopoisk_rating',
                                              'wikipedia_en', 'wikipedia_ru']
    list_select_related = ('imdb', 'kinopoisk')
    list_filter = (ImdbFilter, KinopoiskFilter) + wikipedia_filters
    inlines = [ImdbMovieInline, KinopoiskMovieInline, WikipediaPageInline] + MovieAdmin.inlines

    def imdb_rating(self, obj):
        return obj.imdb.rating

    def kinopoisk_rating(self, obj):
        return obj.kinopoisk.rating


@register(Person, site=site)
class SitesPersonAdmin(SitesAdminMixin, PersonAdmin):  # type: ignore
    list_display = PersonAdmin.list_display + ['imdb_id', 'kinopoisk_id', 'wikipedia_en', 'wikipedia_ru']
    list_select_related = ('imdb', 'kinopoisk')
    list_filter = (ImdbFilter, KinopoiskFilter) + wikipedia_filters
    inlines = [ImdbPersonInline, KinopoiskPersonInline, WikipediaPageInline] + PersonAdmin.inlines
