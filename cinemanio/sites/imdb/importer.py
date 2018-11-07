import logging
import re
from datetime import date  # noqa
from typing import Tuple, Dict, Optional, List

from dateutil import parser
from imdb import IMDb

from cinemanio.core.models import Movie, Person, Genre, Language, Country, Role, Cast
from cinemanio.sites.imdb.models import ImdbMovie, ImdbPerson

logger = logging.getLogger(__name__)


class ImdbImporterBase:
    """
    Base importer of data from IMDB
    """
    _imdb_object = None

    logger = None

    def __init__(self, instance, imdb_id):
        self.object = instance
        self.imdb = IMDb()
        self.imdb_id = int(imdb_id)

    @property
    def imdb_object(self):
        """
        Make request to imdb and save response to cache
        """
        if not self._imdb_object:
            self._imdb_object = self.get_imdb_object(self.imdb_id)
        return self._imdb_object

    @property
    def model(self):
        raise NotImplementedError()

    def get_imdb_object(self, imdb_id):
        raise NotImplementedError()

    def get_name_parts(self, name) -> Tuple[str, str]:
        name_parts = name.split(', ')
        if len(name_parts) >= 2:
            last, first = name_parts[:2]
        else:
            last, first = '', name_parts[0]
        return last, first

    def apply_remote_data(self, data, roles) -> None:
        """
        Update object with remote data
        """
        raise NotImplementedError

    def get_remote_data(self) -> Dict[str, str]:
        """
        Return dict with imdb data
        """
        raise NotImplementedError

    def get_applied_data(self, roles=False) -> Dict[str, str]:
        """
        Retrieve remote data and apply it to the self.object
        :param roles: if True sync cast with existing, if 'all', create non-existing cast
        :return: remote data
        """
        data = self.get_remote_data()
        self.apply_remote_data(data, roles=roles)
        return data


class ImdbPersonImporter(ImdbImporterBase):
    """
    Importer of person data from IMDB
    """
    model = Person

    def get_imdb_object(self, imdb_id):
        return self.imdb.get_person(imdb_id)

    def apply_remote_data(self, data, roles) -> None:
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
                self._add_roles(roles)

    def get_remote_data(self) -> Dict[str, str]:
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

    def _get_name_eng(self) -> Tuple[str, str]:
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

    def _get_date(self, field) -> Optional[date]:
        date_str = self.imdb_object.data.get(field)
        try:
            return parser.parse(date_str).date()
        except (ValueError, TypeError):
            return None

    def _get_country(self) -> Optional[int]:
        birth_notes = self.imdb_object.data.get('birth notes', '')
        for country in Country.objects.select_related('imdb').all():
            if country.imdb.name and birth_notes.find(country.imdb.name) != -1:
                return country.id
        return None

    def _add_roles(self, roles) -> None:
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
            # (Role.ACTOR_ID, 'self'),
            (Role.PRODUCER_ID, 'producer'),
            (Role.EDITOR_ID, 'editor movie'),
            (Role.EDITOR_ID, 'editor'),
            (Role.SCENARIST_ID, 'writer'),
            (Role.SCENARIST_ID, 'writer movie'),
            (Role.SCENARIST_ID, 'writer tv'),
            (Role.SCENARIST_ID, 'writer short'),
        )
        for role_id, imdb_key in role_list:
            role = Role.objects.get(id=role_id)
            for filmography in self.imdb_object.data['filmography']:
                for imdb_movie in filmography.get(imdb_key, []):
                    try:
                        self.create_cast(role, imdb_movie)
                    except (Movie.DoesNotExist, Movie.MultipleObjectsReturned):
                        # skip series and video games
                        if (roles == 'all' and imdb_movie.data['kind'] not in ['tv series', 'video game']
                                and 'Series' not in imdb_movie.notes):
                            movie = self.create_movie(imdb_movie)
                            self.create_cast(role, imdb_movie, movie)
                        else:
                            continue

    def create_cast(self, role: Role, imdb_movie, movie=None) -> Cast:
        imdb_id = self.imdb.get_imdbID(imdb_movie)
        title = imdb_movie.data['title']
        year = imdb_movie.data.get('year')

        # if writer has note story or novel, then it must be a
        if role.is_scenarist() and re.search(r'story|novel', imdb_movie.notes):
            role = Role.objects.get_author()

        try:
            if movie is None:
                # get movie by imdb_id
                movie = Movie.objects.get(imdb__id=imdb_id)
        except Movie.DoesNotExist:
            try:
                # get cast by movie name among person's movies
                cast = self.object.career.get(movie__title_en=title, role=role)
                created = False
            except Cast.DoesNotExist:
                try:
                    # TODO: improve performance of this query
                    # get cast by role name and movie year among person's movies
                    cast = self.object.career.get(name_en__iexact=imdb_movie.notes.lower(), role=role,
                                                  movie__imdb=None,
                                                  movie__year__gte=year - 1,
                                                  movie__year__lte=year + 1)
                    created = False
                except (Cast.DoesNotExist, TypeError):
                    # get cast by movie name and year among all movies
                    movie = Movie.objects.get(title_en=title, year=year, imdb__id=None)
                    cast, created = Cast.objects.get_or_create(person=self.object, movie=movie, role=role)
                else:
                    # update movie to make it more imdb friendly in case we found it using role name only
                    cast.movie.title_en = title
                    cast.movie.year = year
                    cast.movie.save()
        else:
            cast, created = Cast.objects.get_or_create(person=self.object, movie=movie, role=role)

        ImdbMovie.objects.update_or_create(movie=cast.movie, defaults={'id': int(imdb_id)})

        # save name of role for actors
        if role.is_actor() and imdb_movie.notes and not cast.name_en:
            cast.name_en = imdb_movie.notes
            cast.save(update_fields=['name_en'])

        if created:
            logger.info(f'Create cast for person {self.object} in movie {cast.movie} with role {role}',
                        extra=dict(person=self.object.id, movie=cast.movie.id, cast=cast.id))
        return cast

    def create_movie(self, imdb_movie) -> Movie:
        imdb_id = self.imdb.get_imdbID(imdb_movie)
        title = imdb_movie.data['title']
        year = imdb_movie.data.get('year')
        movie = Movie.objects.create(title=title, year=year)
        ImdbMovie.objects.create(movie=movie, id=imdb_id)
        logger.info(f'Create movie {movie} from person {self.object}',
                    extra=dict(person=self.object.id, movie=movie.id))
        return movie


class ImdbMovieImporter(ImdbImporterBase):
    """
    Importer of movie data from IMDB
    """
    model = Movie

    def get_imdb_object(self, imdb_id):
        return self.imdb.get_movie(imdb_id)

    def apply_remote_data(self, data, roles) -> None:
        """
        Update movie with remote data
        """
        if data.get('imdb_rating', None):
            self.object.imdb.rating = data['imdb_rating']

        # fields should be updated even if there is value
        for field in ['title_en', 'year', 'runtime']:
            if data.get(field, None) is not None:
                setattr(self.object, field, data[field])

        # fields should be updated only if there is no value
        for field in ['title_ru', 'title_original']:
            if data.get(field, None) is not None and not getattr(self.object, field):
                setattr(self.object, field, data[field])

        # if object in database, we can update m2m fields
        if self.object.id:
            for field in ['genres', 'countries', 'languages']:
                getattr(self.object, field).set(
                    set(data[field]) | set(getattr(self.object, field).values_list('id', flat=True)))

            if roles:
                self._add_roles(roles)

    def get_remote_data(self) -> Dict[str, str]:
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
            'title_en': self.imdb_object.data.get('title'),
            'title_ru': self._get_title('ru'),
            # 'title_original': self._get_title('en'),
            # 'russia_start': self._get_russia_start(self.imdb),
            'year': self.imdb_object.data.get('year'),
            'imdb_rating': self.imdb_object.data.get('rating'),
            'runtime': runtimes,
            'genres': self._get_genres() + self._get_types(),
            'countries': self._get_countries(),
            'languages': self._get_languages(),
        }
        return data

    # def _get_russia_start(self, imdb) -> Optional[date]:
    #     releases = imdb.get_movie_release_dates(self.imdb_id)
    #     for release in releases['data'].get('release dates', []):
    #         release = release.split('::')
    #         if len(release) != 2:
    #             release += release
    #         if re.findall(r'russia', release[0], re.I):
    #             try:
    #                 return parser.parse(re.sub(r'^(\d+ \w+ \d{4}).*$', r'\1', release[1])).date()
    #             except ValueError:
    #                 pass
    #     return None

    def _get_title(self, language) -> str:

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

    def _get_types(self) -> List[int]:
        ids = []  # type: List[int]
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

    def _get_genres(self) -> List[int]:
        return self._get_m2m_ids(Genre, self.imdb_object.data.get('genres', []))

    def _get_languages(self) -> List[int]:
        return self._get_m2m_ids(Language, self.imdb_object.data.get('languages', []))

    def _get_countries(self) -> List[int]:
        return self._get_m2m_ids(Country, self.imdb_object.data.get('countries', []),
                                 lambda i: i.replace('United States', 'USA'))

    def _get_m2m_ids(self, model, values, callback=lambda i: i) -> List[int]:
        ids = model.objects.filter(imdb__name__in=[callback(i) for i in values]).values_list('id', flat=True)
        if len(ids) != len(values):
            logger.error('Unable to find some of imdb properties',
                         extra=dict(type=model.__name__, values=values))
        return list(ids)

    def _add_roles(self, roles) -> None:
        """
        Find persons of current movie by imdb_id or name:
        1. Trying find person by imdb_id
        2. Trying find person by name among movie's persons
        3. Trying find person by name among all persons
        If found update imdb_id of person, create/update role and role's name_en
        """
        role_list = (
            (Role.DIRECTOR_ID, 'directors'),
            (Role.ACTOR_ID, 'cast'),
            (Role.PRODUCER_ID, 'producers'),
            (Role.EDITOR_ID, 'editors'),
            (Role.SCENARIST_ID, 'writers'),
            (Role.OPERATOR_ID, 'cinematographers'),
        )
        for role_id, imdb_key in role_list:
            role = Role.objects.get(id=role_id)
            for imdb_person in self.imdb_object.data.get(imdb_key, []):
                # skip person without name
                if 'name' not in imdb_person.data:
                    continue

                try:
                    self.create_cast(role, imdb_person)
                except (Person.DoesNotExist, Person.MultipleObjectsReturned):
                    if roles == 'all':
                        person = self.create_person(imdb_person)
                        self.create_cast(role, imdb_person, person)
                    else:
                        continue

    def create_cast(self, role: Role, imdb_person, person=None) -> Cast:
        """
        Create or update Cast instance for imdb person
        """
        imdb_id = self.imdb.get_imdbID(imdb_person)
        last, first = self.get_name_parts(imdb_person.data['name'])

        # if writer has note story or novel, then it must be a
        if role.is_scenarist() and re.search(r'story|novel', imdb_person.notes):
            role = Role.objects.get_author()

        try:
            if person is None:
                # get person by imdb_id
                person = Person.objects.get(imdb__id=imdb_id)
        except Person.DoesNotExist:
            try:
                # get person by name among movie's persons and save imdb_id for future
                cast = self.object.cast.get(person__first_name_en=first, person__last_name_en=last, role=role)
                created = False
            except Cast.DoesNotExist:
                # get person by name among all persons
                # TODO: remove this DANGEROUS behaviour or add some other checks
                person = Person.objects.get(first_name_en=first, last_name_en=last, imdb__id=None)
                cast, created = Cast.objects.get_or_create(movie=self.object, person=person, role=role)
        else:
            cast, created = Cast.objects.get_or_create(movie=self.object, person=person, role=role)

        ImdbPerson.objects.update_or_create(person=cast.person, defaults={'id': int(imdb_id)})

        # save name of role for actors
        if role.is_actor() and imdb_person.notes and not cast.name_en:
            cast.name_en = imdb_person.notes
            cast.save(update_fields=['name_en'])

        if created:
            logger.info(f'Create cast for person {cast.person} in movie {self.object} with role {role}',
                        extra=dict(person=cast.person.id, movie=self.object.id, cast=cast.id))
        return cast

    def create_person(self, imdb_person) -> Person:
        imdb_id = self.imdb.get_imdbID(imdb_person)
        last, first = self.get_name_parts(imdb_person.data['name'])
        person = Person.objects.create(first_name=first, last_name=last)
        ImdbPerson.objects.create(person=person, id=imdb_id)
        logger.info(f'Create person {person} from movie {self.object}',
                    extra=dict(person=person.id, movie=self.object.id))
        return person
