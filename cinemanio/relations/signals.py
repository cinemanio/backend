from django.dispatch import Signal
from django.dispatch import receiver

from cinemanio.relations.models import MovieRelation, PersonRelation, UserRelation
from cinemanio.relations.tasks import recount_familiar_objects, delete_empty_relations, recount_object_relations

relation_changed = Signal(providing_args=['instance', 'code', 'request'])


@receiver(relation_changed, sender=MovieRelation)
@receiver(relation_changed, sender=PersonRelation)
@receiver(relation_changed, sender=UserRelation)
def delete_empty_relations_signal(sender, instance, **_):
    """
    Delay removing empty relation (all False)
    """
    delete_empty_relations.delay(sender, instance.id)


@receiver(relation_changed, sender=MovieRelation)
@receiver(relation_changed, sender=PersonRelation)
def recount_familiar_objects_signal(sender, instance, **_):
    """
    Delay recount of user familiar objects
    """
    recount_familiar_objects.delay(sender, instance.user.id)


@receiver(relation_changed, sender=MovieRelation)
@receiver(relation_changed, sender=PersonRelation)
def recount_relations_signal(sender, instance, **_):
    """
    Run recount_object_relations synchronously to provide immediate counts in response
    """
    recount_object_relations(sender, instance)
