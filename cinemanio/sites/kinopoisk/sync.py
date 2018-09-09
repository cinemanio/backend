import operator
from functools import reduce

from alphabet_detector import AlphabetDetector
from django.db.models import Q
from kinopoisk.movie import Movie as KinoMovie
from kinopoisk.person import Person as KinoPerson

from cinemanio.core.models import Movie, Genre, Country, Role, Cast
from cinemanio.images.models import ImageWrongType, ImageType


def get_q_filter(**kwargs):
    return reduce(operator.or_, [Q(**{name: value}) for name, value in kwargs.items() if value])


class SyncBase:
    _remote_obj = None

    @property
    def model(self):
        raise NotImplementedError()

    @property
    def remote_obj(self):
        if self._remote_obj is None:
            self._remote_obj = self.model(id=self.id)
        return self._remote_obj

    def sync_image(self, url, instance, **kwargs):
        try:
            downloaded = instance.images.get_or_download(url, **kwargs)[1]
            if downloaded:
                self.logger.info(f'Image "{url}" downloaded for {instance} successfully')
            else:
                self.logger.info(f'Found already downloaded image "{url}" for {instance}')
        except ImageWrongType:
            self.logger.error(f'Error saving image. Need jpeg, not "{url}"')


class PersonSyncMixin(SyncBase):
    """
    Sync mixin of person data from Kinopoisk
    """
    model = KinoPerson

    def sync_details(self):
        self.remote_obj.get_content('main_page')

        self.info = self.remote_obj.information

    def sync_images(self):
        self.remote_obj.get_content('photos')

        for url in self.remote_obj.photos:
            self.sync_image(url, self.person, type=ImageType.PHOTO)

        self.logger.info(f'{len(self.remote_obj.photos)} photos imported successfully for person {self.person}')

    def sync_trailers(self):
        pass

    def sync_career(self, roles=True):
        """
        Find movies of current person by kinopoisk_id or title:
        1. Trying find movie by kinopoisk_id
        2. Trying find movie by title among person's movies
        3. Trying find movie by title among all movies
        If found update kinopoisk_id of movie, create/update role and role's role_en
        """
        self.remote_obj.get_content('main_page')
        role_map = {
            'actor': Role.ACTOR_ID,
            'director': Role.DIRECTOR_ID,
            'writer': Role.SCENARIST_ID,
            'editor': Role.EDITOR_ID,
            'hrono_titr_male': Role.ACTOR_ID,  # Актер: Хроника, В титрах не указан
            # 'himself': Role.ACTOR_ID,
        }
        for role_key, person_roles in self.remote_obj.career.items():
            role_id = role_map.get(role_key, None)
            if role_id is None:
                continue
            role = Role.objects.get(id=role_id)
            for person_role in person_roles:
                try:
                    self.create_cast(role, person_role)
                except (Movie.DoesNotExist, Movie.MultipleObjectsReturned):
                    # skip series
                    if roles == 'all' and not person_role.movie.series:
                        movie = self.create_movie(person_role)
                        self.create_cast(role, person_role, movie)
                    else:
                        continue

    def create_cast(self, role, person_role, movie=None):
        cast = created = None

        try:
            if movie is None:
                # get movie by kinopoisk_id
                movie = Movie.objects.get(kinopoisk__id=person_role.movie.id)
            cast, created = Cast.objects.get_or_create(person=self.person, movie=movie, role=role)
        except Movie.DoesNotExist:
            if person_role.movie.title or person_role.movie.title_en:
                try:
                    # get movie by name among person's movies
                    cast = self.person.career.get(
                        get_q_filter(movie__title_en=person_role.movie.title_en,
                                     movie__title_ru=person_role.movie.title),
                        movie__year=person_role.movie.year, role=role)
                    movie = cast.movie
                    created = False
                except Cast.DoesNotExist:
                    # get movie by name among all movies
                    movie = Movie.objects.get(
                        get_q_filter(title_en=person_role.movie.title_en,
                                     title_ru=person_role.movie.title),
                        year=person_role.movie.year, kinopoisk=None)
                    cast, created = Cast.objects.get_or_create(person=self.person, movie=movie, role=role)

        if movie and created:
            self.logger.info(f'Create cast for person {self.person} in movie {movie} with role {role}')

        # save kinopoisk ID for movie
        if movie:
            from cinemanio.sites.kinopoisk.models import KinopoiskMovie
            KinopoiskMovie.objects.update_or_create(movie=movie, defaults={'id': person_role.movie.id})

        # save name of role for actors
        if role.is_actor() and person_role.name and cast:
            ad = AlphabetDetector()
            field_name = 'name_ru' if ad.is_cyrillic(person_role.name) else 'name_en'
            if not getattr(cast, field_name):
                setattr(cast, field_name, person_role.name)
                cast.save(update_fields=[field_name])
        return cast

    def create_movie(self, person_role):
        from cinemanio.sites.kinopoisk.models import KinopoiskMovie
        movie = Movie.objects.create(
            title_ru=person_role.movie.title,
            title_en=person_role.movie.title_en,
            year=person_role.movie.year,
        )
        KinopoiskMovie.objects.create(movie=movie, id=person_role.movie.id)
        self.logger.info(f'Create movie {movie} from person {self.person}')
        return movie


class MovieSyncMixin(SyncBase):
    """
    Sync mixin of movie data from Kinopoisk
    """
    model = KinoMovie

    def sync_details(self):
        self.remote_obj.get_content('main_page')

        fields_map = (
            ('info', 'plot'),
            ('rating', 'rating'),
            ('votes', 'votes'),
        )
        for field1, field2 in fields_map:
            setattr(self, field1, getattr(self.remote_obj, field2))

        fields_map = (
            ('title_ru', 'title'),
            ('title_en', 'title_en'),
            ('year', 'year'),
            ('runtime', 'runtime'),
        )

        for field1, field2 in fields_map:
            value = getattr(self.remote_obj, field2)
            if value and not getattr(self.movie, field1):
                setattr(self.movie, field1, value)

        data = {
            'genres': self._get_genres(),
            'countries': self._get_countries(),
        }

        for field, ids in data.items():
            getattr(self.movie, field).set(
                set(ids) | set(getattr(self.movie, field).values_list('id', flat=True)))

    def _get_genres(self):
        return self._get_m2m_ids(Genre, self.remote_obj.genres)

    def _get_countries(self):
        return self._get_m2m_ids(Country, self.remote_obj.countries)

    def _get_m2m_ids(self, model, values):
        ids = model.objects.filter(kinopoisk__name__in=values).values_list('id', flat=True)
        if len(ids) != len(values):
            self.logger.error("Unable to find some of kinopoisk {}: {}".format(model.__name__, values))
        return ids

    def sync_images(self):
        self.remote_obj.get_content('posters')

        for url in self.remote_obj.posters:
            self.sync_image(url, self.movie, type=ImageType.POSTER)

        self.logger.info(f'{len(self.remote_obj.posters)} posters imported successfully for movie {self.movie}')

    def sync_trailers(self):
        pass

    def sync_cast(self):
        """
        Find persons of current movie by kinopoisk_id or name:
        1. Trying find person by kinopoisk_id
        2. Trying find person by name among movie's persons
        3. Trying find person by name among all persons
        If found update kinopoisk_id of person, create/update role and role's name_en
        """
        # self.remote_obj.get_content('cast')

#         role_list = (
#             (DIRECTOR_ID, 'director'),
#             (ACTOR_ID, 'cast'),
#             (PRODUCER_ID, 'producer'),
#             (EDITOR_ID, 'editor'),
#             (SCENARIST_ID, 'writer'),
#         )
#         for role_id, imdb_key in role_list:
#             role = Role.objects.get(id=role_id)
#             for imdb_person in self.imdb_object.data.get(imdb_key, []):
#                 imdb_id = self.imdb.get_imdbID(imdb_person)
#                 last, first = self.get_name_parts(imdb_person.data['name'])
#                 cast = person = None
#
#                 # if writer has note story or novel, then it must be a
#                 if role.is_scenarist() and re.search(r'story|novel', imdb_person.notes):
#                     role = Role.objects.get_author()
#
#                 try:
#                     # get person by imdb_id
#                     person = Person.objects.get(imdb__id=imdb_id)
#                     cast, created = Cast.objects.get_or_create(movie=self.object, person=person, role=role)
#                 except Person.DoesNotExist:
#                     try:
#                         # get person by name among movie's persons and save imdb_id for future
#                         cast = self.object.cast.get(person__first_name_en=first, person__last_name_en=last, role=role)
#                         person = cast.person
#                         created = False
#                     except Cast.DoesNotExist:
#                         try:
#                             # get person by name among all persons
#                             person = Person.objects.get(first_name_en=first, last_name_en=last, imdb__id=None)
#                             cast, created = Cast.objects.get_or_create(movie=self.object, person=person, role=role)
#                         except (Person.DoesNotExist, Person.MultipleObjectsReturned):
#                             continue
#
#                 if person and created:
#                     self.logger.info(
#                         'Create role for person %s in movie %s with role %s' % (person, self.object, role))
#
#                 # save imdb_id for future
#                 if person and not person.imdb.id:
#                     person.imdb.id = imdb_id
#                     person.save(update_fields=['imdb_id'])
#
#                 # save name of role for actors
#                 if role.is_actor() and imdb_person.currentRole and cast and not cast.name_en:
#                     if isinstance(imdb_person.currentRole, RolesList):
#                         # may be it's better to make to different roles
#                         # test movie http://www.imdb.com/title/tt0453249/
#                         cast.name_en = ' / '.join(
#                             [cr.data['name'] for cr in imdb_person.currentRole if cr.data.get('name')])
#                     elif isinstance(imdb_person.currentRole, Character):
#                         cast.name_en = imdb_person.currentRole.data['name']
#                     cast.save(update_fields=['name_en'])
