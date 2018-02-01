from django.db import models
from django.utils.translation import ugettext_lazy as _
from kinopoisk.movie import Movie as KinoMovie
from kinopoisk.person import Person as KinoPerson

from cinemanio.core.models import Movie, Person


class KinopoiskBase(models.Model):
    info = models.TextField(_('Kinopoisk information'), blank=True, default='')

    class Meta:
        abstract = True


class UrlMixin:
    @property
    def url(self):
        return self.link.format(id=self.id)


class KinopoiskMovie(KinopoiskBase, UrlMixin):
    """
    Kinopoisk movie model
    """
    id = models.PositiveIntegerField(_('Kinopoisk ID'), primary_key=True)
    rating = models.FloatField(_('Kinopoisk rating'), null=True, db_index=True, blank=True)
    movie = models.OneToOneField(Movie, related_name='kinopoisk', on_delete=models.CASCADE)

    link = 'http://www.kinopoisk.ru/film/{id}/'

    def sync_details(self):
        movie = KinoMovie(id=self.id)
        movie.get_content('main_page')
        self.info = movie.plot
        self.rating = movie.rating

    def sync_images(self):
        pass

    def sync_trailers(self):
        pass

    def sync_cast(self):
        pass


class KinopoiskPerson(KinopoiskBase, UrlMixin):
    """
    Kinopoisk person model
    """
    id = models.PositiveIntegerField(_('Kinopoisk ID'), primary_key=True)
    person = models.OneToOneField(Person, related_name='kinopoisk', on_delete=models.CASCADE)

    link = 'http://www.kinopoisk.ru/name/{id}/'

    def sync_details(self):
        person = KinoPerson(id=self.id)
        person.get_content('main_page')
        self.info = person.information

    def sync_images(self):
        pass

    def sync_trailers(self):
        pass

    def sync_career(self):
        pass
