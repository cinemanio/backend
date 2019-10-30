import re

from django.contrib.contenttypes.models import ContentType

from cinemanio.celery import app
from cinemanio.core.models import Movie, Person
from cinemanio.sites.imdb.models import ImdbMovie, ImdbPerson
from cinemanio.sites.imdb.exceptions import ImdbSeriesEpisodeFound
from cinemanio.sites.exceptions import SiteIDDoesNotExist


@app.task
def sync_movie(movie_id, roles=True):
    """
    Sync and save movie with imdb
    """
    sync(Movie, ImdbMovie, movie_id, roles)


@app.task
def sync_person(person_id, roles=True):
    """
    Sync and save person with imdb
    """
    sync(Person, ImdbPerson, person_id, roles)


def sync(model, imdb_model, object_id, roles):
    instance = model.objects.get(pk=object_id)
    try:
        instance.imdb
    except imdb_model.DoesNotExist:
        imdb_model.objects.create_for(instance)
    finally:
        try:
            instance.imdb.sync(roles=roles)
            instance.imdb.save()
            instance.save()
        except (SiteIDDoesNotExist, ImdbSeriesEpisodeFound):
            instance.imdb.delete()
        except imdb_model.DoesNotExist:
            pass


@app.task
def search_link(content_type_id, object_id, links, html):
    """
    Search IMDb link in links, attach one if found
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

    for link in links + [html]:
        m = re.findall(rf'https?://(?:www\.)?imdb\.com/{prefix}(\d+)/?', link)
        if m:
            model.objects.safe_create(m[0], instance)
            break
