from django.db import models
from django.utils.translation import ugettext_lazy as _

from cinemanio.core.models import Movie, Person


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
    movie = models.OneToOneField(Movie, related_name='imdb', on_delete=models.CASCADE)

    link = 'http://www.imdb.com/title/tt{id}/'


class ImdbPerson(models.Model, UrlMixin):
    """
    Imdb person model
    """
    id = models.PositiveIntegerField(_('IMDb ID'), primary_key=True)
    person = models.OneToOneField(Person, related_name='imdb', on_delete=models.CASCADE)

    link = 'http://www.imdb.com/name/nm{id}/'
