import re
from django.contrib.contenttypes.models import ContentType

from cinemanio.celery import app
from cinemanio.core.models import Movie, Person
from cinemanio.sites.imdb.models import ImdbMovie, ImdbPerson


@app.task
def sync_movie(movie_id, roles=True):
    """
    Sync and save movie with imdb
    """
    movie = Movie.objects.get(pk=movie_id)
    try:
        movie.imdb
    except ImdbMovie.DoesNotExist:
        ImdbMovie.objects.create_for(movie)
    finally:
        try:
            movie.imdb.sync(roles=roles)
            movie.imdb.save()
            movie.save()
        except ImdbMovie.DoesNotExist:
            pass


@app.task
def sync_person(person_id, roles=True):
    """
    Sync and save person with imdb
    """
    person = Person.objects.get(pk=person_id)
    try:
        person.imdb
    except ImdbPerson.DoesNotExist:
        ImdbPerson.objects.create_for(person)
    finally:
        try:
            person.imdb.sync(roles=roles)
            person.imdb.save()
            person.save()
        except ImdbPerson.DoesNotExist:
            pass


@app.task
def search_link(content_type_id, object_id, links):
    """
    Search IMDb link in links, attach one if found and delay sync task
    """
    instance = ContentType.objects.get(id=content_type_id).get_object_for_this_type(id=object_id)
    if isinstance(instance, Movie):
        prefix = 'title/tt'
        model = ImdbMovie
    elif isinstance(instance, Person):
        prefix = 'name/nm'
        model = ImdbPerson
    else:
        raise TypeError(f"Type of instance attribute is unknown: {type(instance)}")

    for link in links:
        m = re.findall(rf'https?://(?:www\.)?imdb\.com/{prefix}(\d+)/?', link)
        if m:
            model.objects.get_or_create(id=m[0], defaults={instance._meta.model_name: instance})
            break
