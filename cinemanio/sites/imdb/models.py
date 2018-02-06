from django.db import models
from django.utils.translation import ugettext_lazy as _

from cinemanio.core.models import Movie, Person, Genre, Language, Country


class UrlMixin:
    @property
    def url(self):
        return self.link.format(id=f'{self.id:07}')


class ImdbMovie(models.Model, UrlMixin):
    """
    Imdb movie model
    """
    id = models.PositiveIntegerField(_('IMDb ID'), primary_key=True)
    rating = models.FloatField(_('IMDb rating'), null=True, db_index=True, blank=True)
    votes = models.PositiveIntegerField(_('IMDb votes number'), null=True, blank=True)
    movie = models.OneToOneField(Movie, related_name='imdb', on_delete=models.CASCADE)

    link = 'http://www.imdb.com/title/tt{id}/'

    def sync(self, roles=False):
        from cinemanio.sites.imdb.importer import ImdbMovieImporter
        ImdbMovieImporter(self.movie, self.id).get_applied_data(roles=roles)


class ImdbPerson(models.Model, UrlMixin):
    """
    Imdb person model
    """
    id = models.PositiveIntegerField(_('IMDb ID'), primary_key=True)
    person = models.OneToOneField(Person, related_name='imdb', on_delete=models.CASCADE)

    link = 'http://www.imdb.com/name/nm{id}/'

    def sync(self, roles=False):
        from cinemanio.sites.imdb.importer import ImdbPersonImporter
        ImdbPersonImporter(self.person, self.id).get_applied_data(roles=roles)


class ImdbPropBase(models.Model):
    name = models.CharField(_('IMDb name'), max_length=50, null=True, unique=True)

    class Meta:
        abstract = True


class ImdbGenre(ImdbPropBase):
    genre = models.OneToOneField(Genre, related_name='imdb', on_delete=models.CASCADE)


class ImdbLanguage(ImdbPropBase):
    language = models.OneToOneField(Language, related_name='imdb', on_delete=models.CASCADE)
    code = models.CharField(_('IMDb code'), max_length=2, null=True, unique=True)


class ImdbCountry(ImdbPropBase):
    country = models.OneToOneField(Country, related_name='imdb', on_delete=models.CASCADE)
    code = models.CharField(_('IMDb code'), max_length=2, null=True, unique=True)
