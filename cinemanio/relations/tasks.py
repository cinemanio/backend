from cinemanio.celery import app
from cinemanio.relations.models import MovieRelation, PersonRelation, UserRelationCount
from cinemanio.users.models import User


@app.task
def recount_familiar_objects(model, user_id):
    """
    Recount familiar movies | persons for user
    """
    user = User.objects.get(pk=user_id)

    count = UserRelationCount.objects.get_or_create(object=user)[0]

    if model == MovieRelation:
        count.movies = user.familiar_movies.count()
    elif model == PersonRelation:
        count.persons = user.familiar_persons.count()
    count.save()


@app.task
def delete_empty_relations(model, instance_id):
    """
    Delete record if all relations are False
    """
    instance = model.objects.get(pk=instance_id)
    relation = False
    for code in instance.codes:
        relation |= getattr(instance, code)

    if not relation:
        instance.delete()


@app.task
def recount_object_relations(model, instance):
    """
    Recount relations for movie | person
    """
    relations_counts = {}
    for code in instance.codes:
        relations_counts[code] = model.objects.filter(object_id=instance.object.id, **{code: True}).count()
    model.count_model.objects.update_or_create(object_id=instance.object.id, defaults=relations_counts)
