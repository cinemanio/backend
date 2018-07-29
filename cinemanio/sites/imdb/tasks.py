from cinemanio.celery import app
from cinemanio.core.models import Movie, Person


@app.task
def sync_movie(movie_id):
    """
    Sync movie with imdb
    """
    movie = Movie.objects.get(pk=movie_id)
    movie.imdb.sync(roles=True)


@app.task
def sync_person(person_id):
    """
    Sync person with imdb
    """
    person = Person.objects.get(pk=person_id)
    person.imdb.sync(roles=True)
