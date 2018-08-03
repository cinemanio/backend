from django.db import models
from django.utils.translation import ugettext_lazy as _
from imdb import IMDb

from cinemanio.core.models import Movie, Person, Genre, Language, Country
from cinemanio.sites.exceptions import PossibleDuplicate, NothingFound


class UrlMixin:
    @property
    def url(self):
        return self.link.format(id=f'{self.id:07}')


class ImdbBaseManager(models.Manager):
    def create_for(self, instance):
        self.validate_for_search(instance)

        imdb = IMDb()

        try:
            return self.search_using_roles(imdb, instance)
        except NothingFound:
            pass

        try:
            return self.search(imdb, instance)
        except NothingFound:
            pass

        raise NothingFound(f"No IMDb results found for {instance._meta.model_name} ID={instance.id}")

    def validate_for_search(self, instance):
        raise NotImplementedError()

    def search_using_roles(self, imdb, instance):
        raise NotImplementedError()

    def search(self, imdb, instance):
        raise NotImplementedError()

    def safe_create(self, imdb_id, instance):
        instance_type = instance._meta.model_name
        try:
            instance_exist = self.get(id=imdb_id)
            instance_exist_id = getattr(instance_exist, instance_type).id
            raise PossibleDuplicate(
                f"Can not assign IMDb ID={imdb_id} to {instance_type} ID={instance.id}, "
                f"because it's already assigned to {instance_type} ID={instance_exist_id}")
        except self.model.DoesNotExist:
            return self.create(id=imdb_id, **{instance_type: instance})


class ImdbMovieManager(ImdbBaseManager):
    def validate_for_search(self, movie):
        if not movie.title or not movie.year:
            raise ValueError("To be able search IMDb movie it should has at lease title and year")

    def search_using_roles(self, imdb, movie):
        """Search by movie's imdb person"""
        if movie.cast.exclude(person__imdb=None).exists():
            person_imdb_id = movie.cast.exclude(person__imdb=None)[0].person.imdb.id
            person_imdb = imdb.get_person(person_imdb_id)
            for category in person_imdb['filmography']:
                for __, results in category.items():
                    for result in results:
                        if result.data['title'] == movie.title and result.data['year'] == movie.year:
                            return self.safe_create(result.movieID, movie)
        raise NothingFound

    def search(self, imdb, movie):
        """Search by movie's title"""
        for result in imdb.search_movie(movie.title):
            if result.data['year'] == movie.year:
                return self.safe_create(result.movieID, movie)
        raise NothingFound


class ImdbPersonManager(ImdbBaseManager):
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
        # 'sound department',
        # 'thanks',
        # 'visual effects',
        'writer',
        'writers',
    ]

    def validate_for_search(self, person):
        if not person.first_name or not person.last_name:
            raise ValueError("To be able search IMDb person it should has first name and last name")

    def search_using_roles(self, imdb, person):
        """Search by person's imdb movie"""
        if person.career.exclude(movie__imdb=None).exists():
            movie_imdb_id = person.career.exclude(movie__imdb=None)[0].movie.imdb.id
            movie_imdb = imdb.get_movie(movie_imdb_id)
            for category in self.movie_persons_categories:
                for result in movie_imdb.get(category, []):
                    if result.data['name'] == f'{person.last_name}, {person.first_name}':
                        return self.safe_create(result.personID, person)
        raise NothingFound

    def search(self, imdb, person):
        """Search by person's name"""
        for result in imdb.search_person(person.name):
            # TODO: make more complicated check if it's right person
            return self.safe_create(result.personID, person)
        raise NothingFound


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
