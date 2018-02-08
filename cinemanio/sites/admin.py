from django.contrib import admin
from django.contrib.admin import register, TabularInline

from cinemanio.core.admin import MovieAdmin, PersonAdmin
from cinemanio.core.models import Movie, Person
from cinemanio.sites.imdb.models import ImdbMovie, ImdbPerson
from cinemanio.sites.kinopoisk.models import KinopoiskMovie, KinopoiskPerson

admin.site.unregister(Movie)
admin.site.unregister(Person)


class ImdbMovieInline(TabularInline):
    classes = ('collapse', 'collapsed',)
    model = ImdbMovie


class KinopoiskMovieInline(TabularInline):
    classes = ('collapse', 'collapsed',)
    model = KinopoiskMovie


class ImdbPersonInline(TabularInline):
    classes = ('collapse', 'collapsed',)
    model = ImdbPerson


class KinopoiskPersonInline(TabularInline):
    classes = ('collapse', 'collapsed',)
    model = KinopoiskPerson


@register(Movie)
class SitesMovieAdmin(MovieAdmin):
    list_display = MovieAdmin.list_display + ['imdb_id', 'imdb_rating',
                                              'kinopoisk_id', 'kinopoisk_rating']
    inlines = [ImdbMovieInline, KinopoiskMovieInline] + MovieAdmin.inlines

    def imdb_id(self, obj):
        return obj.imdb.id

    def imdb_rating(self, obj):
        return obj.imdb.rating

    def kinopoisk_id(self, obj):
        return obj.kinopoisk.id

    def kinopoisk_rating(self, obj):
        return obj.kinopoisk.rating

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('imdb', 'kinopoisk')


@register(Person)
class SitesPersonAdmin(PersonAdmin):
    list_display = PersonAdmin.list_display + ['imdb_id', 'kinopoisk_id']
    inlines = [ImdbPersonInline, KinopoiskPersonInline] + PersonAdmin.inlines

    def imdb_id(self, obj):
        return obj.imdb.id

    def kinopoisk_id(self, obj):
        return obj.kinopoisk.id

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('imdb', 'kinopoisk')
