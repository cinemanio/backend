import logging

from django.contrib.contenttypes.models import ContentType

from cinemanio.celery import app
from cinemanio.core.models import Movie, Person
from cinemanio.sites.exceptions import PossibleDuplicate, NothingFound
from cinemanio.sites.wikipedia.models import WikipediaPage

logger = logging.getLogger(__name__)


@app.task
def sync_movie(movie_id):
    """
    Sync and save movie with wikipedia
    """
    movie = Movie.objects.get(pk=movie_id)
    sync(movie)


@app.task
def sync_person(person_id):
    """
    Sync and save person with wikipedia
    """
    person = Person.objects.get(pk=person_id)
    sync(person)


def sync(instance):
    for lang in ['en', 'ru']:
        if not instance.wikipedia.filter(lang=lang).exists():
            try:
                WikipediaPage.objects.create_for(instance, lang=lang)
            except (NothingFound, ValueError):
                continue
            except PossibleDuplicate as e:
                logger.warning(e)
                continue

    for page in instance.wikipedia.all():
        page.sync()
        page.save()


@app.task
def search_roles_links(content_type_id, object_id, lang, links):
    """
    Search wikipedia link in links, attach one if found and delay sync task
    """
    instance = ContentType.objects.get(id=content_type_id).get_object_for_this_type(id=object_id)
    if isinstance(instance, Movie):
        linked_instances = instance.persons.all()
    elif isinstance(instance, Person):
        linked_instances = instance.movies.order_by('id')
    else:
        raise TypeError(f"Type of instance attribute is unknown: {type(instance)}")

    for linked_instance in linked_instances:
        try:
            WikipediaPage.objects.create_from_list_for(linked_instance, lang, links)
        except (ValueError, NothingFound):
            continue
