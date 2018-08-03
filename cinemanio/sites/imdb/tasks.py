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
