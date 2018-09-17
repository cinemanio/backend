import logging
from django.db import models
from django.utils.translation import ugettext_lazy as _

from cinemanio.core.models import Movie, Person, Country, Genre
from cinemanio.sites.kinopoisk.sync import PersonSyncMixin, MovieSyncMixin
from cinemanio.sites.models import SitesBaseModel

logger = logging.getLogger(__name__)


class KinopoiskBase(SitesBaseModel):
    info = models.TextField(_('Kinopoisk information'), blank=True, default='')

    class Meta:
        abstract = True

    @property
    def logger(self):
        return logger


class UrlMixin:
    @property
    def url(self):
        return self.link.format(id=self.id)


class KinopoiskMovie(KinopoiskBase, UrlMixin, MovieSyncMixin):
    """
    Kinopoisk movie model
    """
    id = models.PositiveIntegerField(_('Kinopoisk ID'), primary_key=True)
    rating = models.FloatField(_('Kinopoisk rating'), null=True, db_index=True, blank=True)
    votes = models.PositiveIntegerField(_('Kinopoisk votes number'), null=True, blank=True)
    movie = models.OneToOneField(Movie, related_name='kinopoisk', on_delete=models.CASCADE)

    link = 'http://www.kinopoisk.ru/film/{id}/'

    def sync(self, details=False, roles=False, images=False, trailers=False):
        if details:
            self.sync_details()
        if roles:
            self.sync_cast(roles)
        if images:
            self.sync_images()
        if trailers:
            self.sync_trailers()
        super().sync()


class KinopoiskPerson(KinopoiskBase, UrlMixin, PersonSyncMixin):
    """
    Kinopoisk person model
    """
    id = models.PositiveIntegerField(_('Kinopoisk ID'), primary_key=True)
    person = models.OneToOneField(Person, related_name='kinopoisk', on_delete=models.CASCADE)

    link = 'http://www.kinopoisk.ru/name/{id}/'

    def sync(self, details=False, roles=False, images=False, trailers=False):
        if details:
            self.sync_details()
        if roles:
            self.sync_career(roles)
        if images:
            self.sync_images()
        if trailers:
            self.sync_trailers()
        super().sync()


class KinopoiskPropBase(models.Model):
    name = models.CharField(_('Kinopoisk name'), max_length=50, null=True, unique=True)

    class Meta:
        abstract = True


class KinopoiskGenre(KinopoiskPropBase):
    genre = models.OneToOneField(Genre, related_name='kinopoisk', on_delete=models.CASCADE)


class KinopoiskCountry(KinopoiskPropBase):
    country = models.OneToOneField(Country, related_name='kinopoisk', on_delete=models.CASCADE)
