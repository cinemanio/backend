import logging

from cinemanio.celery import app
from cinemanio.core.models import Movie, Person
from cinemanio.sites.exceptions import PossibleDuplicate
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
    if instance.wikipedia.count() == 0:
        for lang in ['en', 'ru']:
            try:
                WikipediaPage.objects.create_for(instance, lang=lang)
            except ValueError:
                continue
            except PossibleDuplicate as e:
                logger.warning(e)
                continue

    for page in instance.wikipedia.all():
        page.sync()
        page.save()
