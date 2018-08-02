from django.db import models
from django.utils.translation import ugettext_lazy as _
from imdb import IMDb

from cinemanio.core.models import Movie, Person, Genre, Language, Country


class UrlMixin:
    @property
    def url(self):
        return self.link.format(id=f'{self.id:07}')


class ImdbMovieManager(models.Manager):
    def create_for(self, movie):
        if not movie.title or not movie.year:
            raise ValueError("To be able search IMDb movie it should has at lease title and year")

        for result in IMDb().search_movie(movie.title):
            if result.data['year'] == movie.year:
                return self.create(id=result.movieID, movie=movie)

        raise ValueError(f"No IMDb movies found for {movie}")


class ImdbPersonManager(models.Manager):
    movie_persons_categories = [
        'cast',
        'art department',
        # 'assistant directors',
        # 'camera department',
        # 'casting department',
        'cinematographers',
        'director',
        'directors',
        'editors',
        # 'make up department',
        'music department',
        'producers',
        # 'production managers',
        'sound department',
        # 'thanks',
        # 'visual effects',
        'writer',
        'writers',
    ]

    def create_for(self, person):
        if not person.first_name or not person.last_name:
            raise ValueError("To be able search IMDb person it should has first name and last name")

        imdb = IMDb()

        # search by person's imdb movie
        if person.career.exclude(movie__imdb=None).exists():
            movie_imdb_id = person.career.exclude(movie__imdb=None)[0].movie.imdb.id
            movie_imdb = imdb.get_movie(movie_imdb_id)
            for category in self.movie_persons_categories:
                for result in movie_imdb.get(category, []):
                    if result.data['name'] == f'{person.last_name}, {person.first_name}':
                        return self.create(id=result.personID, person=person)

        # search by person's name
        for result in imdb.search_person(person.name):
            # TODO: make more complicated check if it's right person
            return self.create(id=result.personID, person=person)

        raise ValueError(f"No IMDb persons found for {person}")


class ImdbMovie(models.Model, UrlMixin):
    """
    Imdb movie model
    """
    id = models.PositiveIntegerField(_('IMDb ID'), primary_key=True)
    rating = models.FloatField(_('IMDb rating'), null=True, db_index=True, blank=True)
    votes = models.PositiveIntegerField(_('IMDb votes number'), null=True, blank=True)
    movie = models.OneToOneField(Movie, related_name='imdb', on_delete=models.CASCADE)

    link = 'http://www.imdb.com/title/tt{id}/'

    objects = ImdbMovieManager()

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

    objects = ImdbPersonManager()

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
