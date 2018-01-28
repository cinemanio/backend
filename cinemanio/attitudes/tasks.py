from celery.task import Task

from cinemanio.attitudes.models import MovieAttitude, PersonAttitude, UserAttitudeCount
from cinemanio.users.models import User


class RecountFamiliarObjects(Task):
    significant_kwargs = []
    herd_avoidance_timeout = 0

    def run(self, sender, user_id, **kwargs):
        user = User.objects.get(id=user_id)

        count = UserAttitudeCount.objects.get_or_create(object=user)[0]

        if sender == MovieAttitude:
            count.movies = user.familiar_movies.count()
        elif sender == PersonAttitude:
            count.persons = user.familiar_persons.count()
        count.save()


class DeleteEmptyAttitudes(Task):
    significant_kwargs = []
    herd_avoidance_timeout = 0

    def run(self, sender, instance_id, **kwargs):
        instance = sender.objects.get(id=instance_id)
        attitude = False
        for code in instance.codes:
            attitude |= getattr(instance, code)

        if not attitude:
            instance.delete()
