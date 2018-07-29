from cinemanio.celery import app
from cinemanio.core.models import Movie, Person


@app.task
def sync_movie(movie_id):
    """
    Sync movie with kinopoisk
    """
    movie = Movie.objects.get(pk=movie_id)
    movie.kinopoisk.sync_details()
    movie.kinopoisk.sync_cast()
    movie.kinopoisk.sync_images()
    movie.kinopoisk.sync_trailers()


@app.task
def sync_person(person_id):
    """
    Sync person with kinopoisk
    """
    person = Person.objects.get(pk=person_id)
    person.kinopoisk.sync_details()
    person.kinopoisk.sync_career()
    person.kinopoisk.sync_images()
    person.kinopoisk.sync_trailers()
