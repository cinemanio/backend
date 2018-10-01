import logging
import operator
from functools import reduce
from typing import List, Tuple, Any

from alphabet_detector import AlphabetDetector
from django.db.models import Q
from kinopoisk.movie import Movie as KinoMovie
from kinopoisk.person import Person as KinoPerson

from cinemanio.core.models import Movie, Person, Genre, Country, Role, Cast
from cinemanio.images.models import ImageWrongType, ImageType

logger = logging.getLogger(__name__)


def get_q_filter(*args, **kwargs):
    q_list = []
    if args:
        q_list = [Q(**arg) for arg in args if "".join(arg.values())]
    elif kwargs:
        q_list = [Q(**{name: value}) for name, value in kwargs.items() if value]
    return reduce(operator.or_, q_list)


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

    def sync_image(self, url, instance, **kwargs) -> None:
        extra = dict(url=url, instance=instance)
        try:
            downloaded = instance.images.get_or_download(url, **kwargs)[1]
            if downloaded:
                logger.info("Image downloaded successfully", extra=extra)
            else:
                logger.info("Found already downloaded image", extra=extra)
        except ImageWrongType:
            logger.error("Error saving image. Need jpeg", extra=extra)

    def get_name_parts(self, name) -> Tuple[str, str]:
        """
        Split name to first and last components
        """
        name_parts = name.split(" ")
        return " ".join(name_parts[:-1]), name_parts[-1]

    def set_movie_m2m_fields(self, movie, remote_obj) -> None:
        data = {"genres": self.get_genres(remote_obj), "countries": self.get_countries(remote_obj)}

        for field, ids in data.items():
            getattr(movie, field).set(set(ids) | set(getattr(movie, field).values_list("id", flat=True)))

    def get_genres(self, remote_obj) -> List[int]:
        return self.get_m2m_ids(Genre, remote_obj.genres)

    def get_countries(self, remote_obj) -> List[int]:
        return self.get_m2m_ids(Country, remote_obj.countries)

    def get_m2m_ids(self, model, values) -> List[int]:
        ids = model.objects.filter(kinopoisk__name__in=values).values_list("id", flat=True)
        if len(ids) != len(values):
            logger.error("Unable to find some of kinopoisk properties", extra=dict(type=model.__name__, values=values))
        return ids

    def get_title_original(self, remote_obj):
        return remote_obj.title_en or remote_obj.title


class PersonSyncMixin(SyncBase):
    """
    Sync mixin of person data from Kinopoisk
    """

    model = KinoPerson

    @property
    def person(self) -> Person:
        raise NotImplementedError()

    def sync_details(self) -> None:
        self.remote_obj.get_content("main_page")

        self.info = self.remote_obj.information

    def sync_images(self) -> None:
        self.remote_obj.get_content("photos")

        for url in self.remote_obj.photos:
            self.sync_image(url, self.person, type=ImageType.PHOTO)

        logger.info(
            f"Photos were imported successfully for person {self.person}",
            extra=dict(count=len(self.remote_obj.photos), person=self.person.id),
        )

    def sync_trailers(self) -> None:
        pass

    def sync_career(self, roles=True) -> None:
        """
        Find movies of current person by kinopoisk_id or title:
        1. Trying find movie by kinopoisk_id
        2. Trying find movie by title among person's movies
        3. Trying find movie by title among all movies
        If found update kinopoisk_id of movie, create/update role and role's role_en
        """
        self.remote_obj.get_content("main_page")
        role_map = {
            "actor": Role.ACTOR_ID,
            "director": Role.DIRECTOR_ID,
            "writer": Role.SCENARIST_ID,
            "editor": Role.EDITOR_ID,
            "hrono_titr_male": Role.ACTOR_ID,  # Актер: Хроника, В титрах не указан
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
                    if roles == "all" and not person_role.movie.series:
                        movie = self.create_movie(person_role)
                        self.create_cast(role, person_role, movie)
                    else:
                        continue

    def create_cast(self, role: Role, person_role, movie=None) -> Cast:
        cast: Any = None
        created: Any = None

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
                        get_q_filter(
                            movie__title_en=person_role.movie.title_en, movie__title_ru=person_role.movie.title
                        ),
                        movie__year=person_role.movie.year,
                        role=role,
                    )
                    movie = cast.movie
                    created = False
                except Cast.DoesNotExist:
                    # get movie by name among all movies
                    movie = Movie.objects.get(
                        get_q_filter(title_en=person_role.movie.title_en, title_ru=person_role.movie.title),
                        year=person_role.movie.year,
                        kinopoisk=None,
                    )
                    cast, created = Cast.objects.get_or_create(person=self.person, movie=movie, role=role)

        if movie and created:
            logger.info(
                f"Create cast for person {self.person} in movie {movie} with role {role}",
                extra=dict(person=self.person.id, movie=movie.id, role=role.id),
            )

        # save kinopoisk ID for movie
        if movie:
            from cinemanio.sites.kinopoisk.models import KinopoiskMovie

            KinopoiskMovie.objects.update_or_create(movie=movie, defaults={"id": person_role.movie.id})

        # save name of role for actors
        if role.is_actor() and person_role.name and cast:
            ad = AlphabetDetector()
            field_name = "name_ru" if ad.is_cyrillic(person_role.name) else "name_en"
            if not getattr(cast, field_name):
                setattr(cast, field_name, person_role.name)
                cast.save(update_fields=[field_name])

        return cast

    def create_movie(self, person_role) -> Movie:
        from cinemanio.sites.kinopoisk.models import KinopoiskMovie

        movie = Movie.objects.create(
            title_ru=person_role.movie.title,
            title_en=person_role.movie.title_en,
            title_original=self.get_title_original(person_role.movie),
            year=person_role.movie.year,
        )
        self.set_movie_m2m_fields(movie, person_role.movie)
        KinopoiskMovie.objects.create(movie=movie, id=person_role.movie.id)
        logger.info(f"Create movie {movie} from person {self.person}", extra=dict(person=self.person.id, movie=movie.id))
        return movie


class MovieSyncMixin(SyncBase):
    """
    Sync mixin of movie data from Kinopoisk
    """

    model = KinoMovie

    @property
    def movie(self) -> Movie:
        raise NotImplementedError()

    def sync_details(self) -> None:
        self.remote_obj.get_content("main_page")

        fields_map = (("info", "plot"), ("rating", "rating"), ("votes", "votes"))  # type: Tuple[Tuple[str, str], ...]
        for field1, field2 in fields_map:
            setattr(self, field1, getattr(self.remote_obj, field2))

        fields_map = (("title_ru", "title"), ("title_en", "title_en"), ("year", "year"), ("runtime", "runtime"))

        for field1, field2 in fields_map:
            value = getattr(self.remote_obj, field2)
            if value and not getattr(self.movie, field1):
                setattr(self.movie, field1, value)

        # assign title_original from any available title
        if not self.movie.title_original:
            self.movie.title_original = self.get_title_original(self.remote_obj)

        self.set_movie_m2m_fields(self.movie, self.remote_obj)

    def sync_images(self) -> None:
        self.remote_obj.get_content("posters")

        for url in self.remote_obj.posters:
            self.sync_image(url, self.movie, type=ImageType.POSTER)

        logger.info(
            f"Posters imported successfully for movie {self.movie}",
            extra=dict(count=len(self.remote_obj.posters), person=self.movie.id),
        )

    def sync_trailers(self):
        pass

    def sync_cast(self, roles=True) -> None:
        """
        Find persons of current movie by kinopoisk_id or name:
        1. Trying find person by kinopoisk_id
        2. Trying find person by name among movie's persons
        3. Trying find person by name among all persons
        If found update kinopoisk_id of person, create/update role and role's name_en
        """
        self.remote_obj.get_content("cast")
        role_map = {
            "actor": Role.ACTOR_ID,
            "director": Role.DIRECTOR_ID,
            "writer": Role.SCENARIST_ID,
            "editor": Role.EDITOR_ID,
            "producer": Role.PRODUCER_ID,
            "composer": Role.COMPOSER_ID,
            "operator": Role.OPERATOR_ID,
        }
        for role_key, person_roles in self.remote_obj.cast.items():
            role_id = role_map.get(role_key, None)
            if role_id is None:
                continue
            role = Role.objects.get(id=role_id)
            for person_role in person_roles:
                try:
                    self.create_cast(role, person_role)
                except (Person.DoesNotExist, Person.MultipleObjectsReturned):
                    if roles == "all":
                        person = self.create_person(person_role)
                        self.create_cast(role, person_role, person)
                    else:
                        continue

    def create_cast(self, role: Role, person_role, person=None) -> Cast:
        cast: Any = None
        created: Any = None

        try:
            if person is None:
                # get person by kinopoisk_id
                person = Person.objects.get(kinopoisk__id=person_role.person.id)
            cast, created = Cast.objects.get_or_create(movie=self.movie, person=person, role=role)
        except Person.DoesNotExist:
            if person_role.person.name or person_role.person.name_en:
                first_ru, last_ru = self.get_name_parts(person_role.person.name)
                first_en, last_en = self.get_name_parts(person_role.person.name_en)
                try:
                    # get person by name among movie's persons
                    cast = self.movie.cast.get(
                        get_q_filter(
                            dict(person__first_name_ru=first_ru, person__last_name_ru=last_ru),
                            dict(person__first_name_en=first_en, person__last_name_en=last_en),
                        ),
                        role=role,
                    )
                    person = cast.person
                    created = False
                except Cast.DoesNotExist:
                    # get person by name among all persons
                    person = Person.objects.get(
                        get_q_filter(
                            dict(first_name_ru=first_ru, last_name_ru=last_ru),
                            dict(first_name_en=first_en, last_name_en=last_en),
                        ),
                        kinopoisk=None,
                    )
                    cast, created = Cast.objects.get_or_create(movie=self.movie, person=person, role=role)

        if person and created:
            logger.info(
                f"Create cast for movie {self.movie} of person {person} with role {role}",
                extra=dict(person=person.id, movie=self.movie.id, role=role.id),
            )

        # save kinopoisk ID for person
        if person:
            from cinemanio.sites.kinopoisk.models import KinopoiskPerson

            KinopoiskPerson.objects.update_or_create(person=person, defaults={"id": person_role.person.id})

        # save notes of role
        if person_role.name and cast:
            ad = AlphabetDetector()
            field_name = "name_ru" if ad.is_cyrillic(person_role.name) else "name_en"
            if not getattr(cast, field_name):
                setattr(cast, field_name, person_role.name)
                cast.save(update_fields=[field_name])

        return cast

    def create_person(self, person_role) -> Person:
        from cinemanio.sites.kinopoisk.models import KinopoiskPerson

        first_ru, last_ru = self.get_name_parts(person_role.person.name)
        first_en, last_en = self.get_name_parts(person_role.person.name_en)
        person = Person.objects.create(
            first_name_ru=first_ru, last_name_ru=last_ru, first_name_en=first_en, last_name_en=last_en
        )
        if person_role.person.name_en == "":
            person.set_transliteratable_fields()
            person.save()
        KinopoiskPerson.objects.create(person=person, id=person_role.person.id)
        logger.info(f"Create person {person} from movie {self.movie}", extra=dict(person=person.id, movie=self.movie.id))
        return person
