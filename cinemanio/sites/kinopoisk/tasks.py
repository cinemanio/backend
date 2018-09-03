import re
from django.contrib.contenttypes.models import ContentType

from cinemanio.celery import app
from cinemanio.core.models import Movie, Person
from cinemanio.sites.kinopoisk.models import KinopoiskMovie, KinopoiskPerson


@app.task
def sync_movie(movie_id):
    """
    Sync movie with kinopoisk
    """
    movie = Movie.objects.get(pk=movie_id)
    movie.kinopoisk.sync()


@app.task
def sync_person(person_id):
    """
    Sync person with kinopoisk
    """
    person = Person.objects.get(pk=person_id)
    person.kinopoisk.sync()


@app.task
def search_link(content_type_id, object_id, links, html):
    """
    Search kinopoisk link in links, attach one if found
    """
    instance = ContentType.objects.get(id=content_type_id).get_object_for_this_type(id=object_id)
    if isinstance(instance, Movie):
        prefix = 'film'
        model = KinopoiskMovie
    elif isinstance(instance, Person):
        prefix = 'name'
        model = KinopoiskPerson
    else:
        raise TypeError(f"Type of instance attribute is unknown: {type(instance)}")

    for link in links + [html]:
        m = re.findall(rf'https?://(?:www\.)?kinopoisk\.ru/{prefix}/(\d+)/?', link)
        if m:
            model.objects.get_or_create(id=m[0], defaults={instance._meta.model_name: instance})
            break
