from cinemanio.celery import app
from cinemanio.core.models import Movie, Person
from cinemanio.sites.wikipedia.models import WikipediaPage


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
            WikipediaPage.objects.create_for(instance, lang=lang)

    for page in instance.wikipedia.all():
        page.sync()
