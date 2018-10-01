from django.contrib import admin
from django.contrib.admin import register, TabularInline
from django.db.models import Prefetch
from django.utils.safestring import mark_safe

from cinemanio.core.admin import get_registered_admin_class
from cinemanio.core.models import Movie, Person
from cinemanio.sites.imdb.models import ImdbMovie, ImdbPerson
from cinemanio.sites.kinopoisk.models import KinopoiskMovie, KinopoiskPerson
from cinemanio.sites.wikipedia.models import WikipediaPage

MovieAdmin = get_registered_admin_class(Movie)
PersonAdmin = get_registered_admin_class(Person)
admin.site.unregister(Movie)
admin.site.unregister(Person)


class InlineBase(TabularInline):
    classes = ("collapse", "collapsed")


class ImdbMovieInline(InlineBase):
    model = ImdbMovie


class KinopoiskMovieInline(InlineBase):
    model = KinopoiskMovie


class ImdbPersonInline(InlineBase):
    model = ImdbPerson


class KinopoiskPersonInline(InlineBase):
    model = KinopoiskPerson


class SitesAdminMixin:
    def imdb_id(self, obj):
        return mark_safe(f'<a href="{obj.imdb.url}" target="_blank">{obj.imdb.id}</a>')

    def kinopoisk_id(self, obj):
        return mark_safe(f'<a href="{obj.kinopoisk.url}" target="_blank">{obj.kinopoisk.id}</a>')

    def wikipedia_en(self, obj):
        return self.wikipedia(obj, "en")

    def wikipedia_ru(self, obj):
        return self.wikipedia(obj, "ru")

    def wikipedia(self, obj, lang):
        try:
            wikipedia = getattr(obj, f"wikipedia_{lang}")[0]
            return mark_safe(f'<a href="{wikipedia.url}" target="_blank">{wikipedia.title}</a>')
        except IndexError:
            return ""

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .prefetch_related(
                Prefetch("wikipedia", to_attr="wikipedia_en", queryset=WikipediaPage.objects.filter(lang="en"))
            )
            .prefetch_related(
                Prefetch("wikipedia", to_attr="wikipedia_ru", queryset=WikipediaPage.objects.filter(lang="ru"))
            )
        )


@register(Movie)
class SitesMovieAdmin(SitesAdminMixin, MovieAdmin):  # type: ignore
    list_display = MovieAdmin.list_display + [
        "imdb_id",
        "imdb_rating",
        "kinopoisk_id",
        "kinopoisk_rating",
        "wikipedia_en",
        "wikipedia_ru",
    ]
    list_select_related = ("imdb", "kinopoisk")
    inlines = [ImdbMovieInline, KinopoiskMovieInline] + MovieAdmin.inlines

    def imdb_rating(self, obj):
        return obj.imdb.rating

    def kinopoisk_rating(self, obj):
        return obj.kinopoisk.rating


@register(Person)
class SitesPersonAdmin(SitesAdminMixin, PersonAdmin):  # type: ignore
    list_display = PersonAdmin.list_display + ["imdb_id", "kinopoisk_id", "wikipedia_en", "wikipedia_ru"]
    list_select_related = ("imdb", "kinopoisk")
    inlines = [ImdbPersonInline, KinopoiskPersonInline] + PersonAdmin.inlines
