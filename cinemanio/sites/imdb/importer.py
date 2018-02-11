import logging
import re

from dateutil import parser
from imdb import IMDb
from imdb.Character import Character
from imdb.utils import RolesList

from cinemanio.core.models import Movie, Person, Genre, Language, Country, Role, Cast
from cinemanio.sites.imdb.models import ImdbMovie, ImdbPerson


class ImdbImporterBase:
    """
    Base importer of data from IMDB
    """
    object = None
    imdb = None
    imdb_id = None
    _imdb_object = None
    model = None

    logger = None

    def __init__(self, object, imdb_id, logger=None):
        self.object = object
        self.imdb = IMDb()
        self.logger = logger or logging
        self.imdb_id = int(imdb_id)

    @property
    def imdb_object(self):
        """
        Make request to imdb and save response to cache
        """
        if not self._imdb_object:
            self._imdb_object = self.get_imdb_object(self.imdb_id)
        return self._imdb_object

    def get_imdb_object(self, id):
        raise NotImplementedError()

    def get_name_parts(self, name):
        name_parts = name.split(', ')
        if len(name_parts) >= 2:
            last, first = name_parts[:2]
        else:
            last, first = '', name_parts[0]
        return last, first

    def apply_remote_data(self, data, roles):
        """
        Update object with remote data
        """
        raise NotImplementedError

    def get_remote_data(self):
        """
        Return dict with imdb data
        """
        raise NotImplementedError

    def get_applied_data(self, roles=False):
        data = self.get_remote_data()
        self.apply_remote_data(data, roles=roles)
        return data


class ImdbPersonImporter(ImdbImporterBase):
    """
    Importer of person data from IMDB
    """
    model = Person

    def get_imdb_object(self, id):
        return self.imdb.get_person(id)

    def apply_remote_data(self, data, roles):
        """
        Update person with remote data
        """
        for field in ['date_birth', 'date_death']:
            setattr(self.object, field, data.get(field, None))

        try:
            self.object.country = Country.objects.get(id=data.get('country'))
        except Country.DoesNotExist:
            pass

        for field in ['first_name_en', 'last_name_en']:
            if not getattr(self.object, field):
                setattr(self.object, field, data.get(field, None))

        # if object in database, we can update m2m fields
        if self.object.id:
            if roles:
                self._add_roles()

    def get_remote_data(self):
        """
        Return dict with essential remote data
        """
        data = {
            'imdb_id': self.imdb_object.personID,
            'first_name_en': self._get_name_eng()[0],
            'last_name_en': self._get_name_eng()[1],
            'date_birth': self._get_date('birth date'),
            'date_death': self._get_date('death date'),
            'country': self._get_country()
        }
        return data

    def _get_name_eng(self):
        name = self.imdb_object.data.get('name')

        # 'name': 'IMDb, Robert De Niro -'
        if name.find('IMDb') != -1:
            name = re.sub(r'IMDb, (.+) -', r'\1', name)
            names = name.split()
            first = names[0]
            last = ' '.join(names[1:]) if len(names) > 1 else ''
        else:
            last, first = self.get_name_parts(name)

        return first, last

    def _get_date(self, field):
        date = self.imdb_object.data.get(field)
        try:
            return parser.parse(date).date()
        except ValueError:
            return None

    def _get_country(self):
        birth_notes = self.imdb_object.data.get('birth notes')
        for country in Country.objects.select_related('imdb'):
            if country.imdb.name and birth_notes.find(country.imdb.name) != -1:
                return country.id
        return None

    def _add_roles(self):
        """
        Find movies of current person by imdb_id or title:
        1. Trying find movie by imdb_id
        2. Trying find movie by title among person's movies
        3. Trying find movie by title among all movies
        If found update imdb_id of movie, create/update role and role's role_en
        """
        role_list = (
            (Role.DIRECTOR_ID, 'director'),
            (Role.DIRECTOR_ID, 'director movie'),
            (Role.ACTOR_ID, 'actor'),
            (Role.ACTOR_ID, 'actress'),
            (Role.PRODUCER_ID, 'producer'),
            (Role.EDITOR_ID, 'editor movie'),
            (Role.SCENARIST_ID, 'writer'),
            (Role.SCENARIST_ID, 'writer movie'),
            (Role.SCENARIST_ID, 'writer tv'),
            (Role.SCENARIST_ID, 'writer short'),
        )
        for role_id, imdb_key in role_list:
            role = Role.objects.get(id=role_id)
            for imdb_movie in self.imdb_object.data.get(imdb_key, []):
                imdb_id = self.imdb.get_imdbID(imdb_movie)
                title = imdb_movie.data['title']
                year = imdb_movie.data.get('year')
                cast = movie = None

                # if writer has note story or novel, then it must be a
                if role.is_scenarist() and re.search(r'story|novel', imdb_movie.notes):
                    role = Role.objects.get_author()

                try:
                    # get movie by imdb_id
                    movie = Movie.objects.get(imdb__id=imdb_id)
                    cast, created = Cast.objects.get_or_create(person=self.object, movie=movie, role=role)
                except Movie.DoesNotExist:
                    try:
                        # get movie by name among person's movies
                        cast = self.object.career.get(movie__title_en=title, role=role)
                        movie = cast.movie
                        created = False
                    except Cast.DoesNotExist:
                        try:
                            # get movie by name among all movies
                            movie = Movie.objects.get(title_en=title, year=year, imdb__id=None)
                            cast, created = Cast.objects.get_or_create(person=self.object, movie=movie, role=role)
                        except (Movie.DoesNotExist, Movie.MultipleObjectsReturned):
                            continue

                if movie and created:
                    self.logger.info(
                        'Create cast for person %s in movie %s with role %s' % (self.object, movie, role))

                if movie:
                    ImdbMovie.objects.update_or_create(movie=movie, defaults={'id': int(imdb_id)})

                # save name of role for actors
                if role.is_actor() and imdb_movie.notes and cast and not cast.name_en:
                    cast.name_en = imdb_movie.notes
                    cast.save(update_fields=['name_en'])


class ImdbMovieImporter(ImdbImporterBase):
    """
    Importer of movie data from IMDB
    """
    model = Movie

    def get_imdb_object(self, id):
        return self.imdb.get_movie(id)

    def apply_remote_data(self, data, roles):
        """
        Update movie with remote data
        """
        if data.get('imdb_rating', None):
            self.object.imdb.rating = data['imdb_rating']

        for field in ['runtime']:
            if data.get(field, None) is not None:
                setattr(self.object, field, data[field])

        for field in ['title_en', 'title_ru', 'title', 'year']:
            if data.get(field, None) is not None and not getattr(self.object, field):
                setattr(self.object, field, data[field])

        # if object in database, we can update m2m fields
        if self.object.id:
            for field in ['genres', 'countries', 'languages']:
                getattr(self.object, field).set(
                    set(data[field]) | set(getattr(self.object, field).values_list('id', flat=True)))

            if roles:
                self._add_roles()

    def get_remote_data(self):
        """
        Return dict with essential remote data
        """
        try:
            runtimes = self.imdb_object.data.get('runtimes')[0].split(':')
            runtimes = int(runtimes[1] if len(runtimes) > 1 else runtimes[0])
        except (IndexError, TypeError):
            runtimes = None

        data = {
            'imdb_id': self.imdb_object.movieID,
            'title': self.imdb_object.data.get('title'),
            'title_ru': self._get_title('ru'),
            'title_en': self._get_title('en'),
            # 'russia_start': self._get_russia_start(self.imdb),
            'year': self.imdb_object.data.get('year'),
            'imdb_rating': self.imdb_object.data.get('rating'),
            'runtime': runtimes,
            'genres': self._get_genres() + self._get_types(),
            'countries': self._get_countries(),
            'languages': self._get_languages(),
        }
        return data

    def _get_russia_start(self, imdb):
        releases = imdb.get_movie_release_dates(self.imdb_id)
        for date in releases['data'].get('release dates', []):
            date = date.split('::')
            if len(date) != 2:
                date += date
            if re.findall(r'russia', date[0], re.I):
                try:
                    return parser.parse(re.sub(r'^(\d+ \w+ \d{4}).*$', r'\1', date[1])).date()
                except ValueError:
                    pass
        return None

    def _get_title(self, language):

        lang_dict = {
            'en': r'(International|UK|USA)',
            'ru': r'(russia|\[ru\])',
        }
        regexp = lang_dict[language]

        # print self.imdb_object.data.get('akas', [])
        for title in self.imdb_object.data.get('akas', []):
            title = title.split('::')
            if len(title) != 2:
                title += title

            if re.findall(regexp, title[1], re.I):
                return re.sub(r'^"(.+)"$', r'\1', title[0].strip())
        return ''

    def _get_types(self):
        ids = []
        data = self.imdb_object.data
        if data.get('color info') and 'Black and White' in data.get('color info') \
                and 'Color' not in data.get('color info'):
            ids += [Genre.BLACK_AND_WHITE_ID]
        if data.get('sound mix') and 'Silent' in data.get('sound mix') \
                or data.get('languages') and 'None' in data.get('languages'):
            ids += [Genre.SILENT_ID]

        if data.get('kind') in ['tv series', 'tv mini series']:
            ids += [Genre.SERIES_ID]
        # 'number of seasons': 5
        # 'series years': '2004-2006'
        # if data.get('number of seasons') > 1 or data.get('series years') and len(data.get('series years')) == 9:
        #     ids += [10]  # сериал
        return ids

    def _get_genres(self):
        return self._get_m2m_ids(Genre, self.imdb_object.data.get('genres', []))

    def _get_languages(self):
        return self._get_m2m_ids(Language, self.imdb_object.data.get('languages', []))

    def _get_countries(self):
        return self._get_m2m_ids(Country, self.imdb_object.data.get('countries', []),
                                 lambda i: i.replace('United States', 'USA'))

    def _get_m2m_ids(self, model, values, callback=lambda i: i):
        ids = model.objects.filter(imdb__name__in=[callback(i) for i in values]).values_list('id', flat=True)
        if len(ids) != len(values):
            self.logger.error("Unable to find some of imdb {}: {}".format(model.__name__, values))
        return list(ids)

    def _add_roles(self):
        """
        Find persons of current movie by imdb_id or name:
        1. Trying find person by imdb_id
        2. Trying find person by name among movie's persons
        3. Trying find person by name among all persons
        If found update imdb_id of person, create/update role and role's name_en
        """
        role_list = (
            (Role.DIRECTOR_ID, 'director'),
            (Role.ACTOR_ID, 'cast'),
            (Role.PRODUCER_ID, 'producer'),
            (Role.EDITOR_ID, 'editor'),
            (Role.SCENARIST_ID, 'writer'),
        )
        for role_id, imdb_key in role_list:
            role = Role.objects.get(id=role_id)
            for imdb_person in self.imdb_object.data.get(imdb_key, []):
                imdb_id = self.imdb.get_imdbID(imdb_person)
                last, first = self.get_name_parts(imdb_person.data['name'])
                cast = person = None

                # if writer has note story or novel, then it must be a
                if role.is_scenarist() and re.search(r'story|novel', imdb_person.notes):
                    role = Role.objects.get_author()

                try:
                    # get person by imdb_id
                    person = Person.objects.get(imdb__id=imdb_id)
                    cast, created = Cast.objects.get_or_create(movie=self.object, person=person, role=role)
                except Person.DoesNotExist:
                    try:
                        # get person by name among movie's persons and save imdb_id for future
                        cast = self.object.cast.get(person__first_name_en=first, person__last_name_en=last, role=role)
                        person = cast.person
                        created = False
                    except Cast.DoesNotExist:
                        try:
                            # get person by name among all persons
                            person = Person.objects.get(first_name_en=first, last_name_en=last, imdb__id=None)
                            cast, created = Cast.objects.get_or_create(movie=self.object, person=person, role=role)
                        except (Person.DoesNotExist, Person.MultipleObjectsReturned):
                            continue

                if person and created:
                    self.logger.info(
                        'Create role for person %s in movie %s with role %s' % (person, self.object, role))

                if person:
                    ImdbPerson.objects.update_or_create(person=person, defaults={'id': int(imdb_id)})

                # save name of role for actors
                if role.is_actor() and imdb_person.currentRole and cast and not cast.name_en:
                    if isinstance(imdb_person.currentRole, RolesList):
                        # may be it's better to make to different roles
                        # test movie http://www.imdb.com/title/tt0453249/
                        cast.name_en = ' / '.join(
                            [cr.data['name'] for cr in imdb_person.currentRole if cr.data.get('name')])
                    elif isinstance(imdb_person.currentRole, Character):
                        cast.name_en = imdb_person.currentRole.data['name']
                    cast.save(update_fields=['name_en'])
