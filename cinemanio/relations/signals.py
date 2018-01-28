from django.dispatch import Signal
from django.dispatch import receiver

from cinemanio.relations.models import MovieRelation, PersonRelation, UserRelation
from cinemanio.relations.tasks import RecountFamiliarObjects, DeleteEmptyRelations

relation_changed = Signal(providing_args=['instance', 'code', 'request'])


@receiver(relation_changed, sender=MovieRelation)
@receiver(relation_changed, sender=PersonRelation)
@receiver(relation_changed, sender=UserRelation)
def delete_empty_relations(sender, instance, **kwargs):
    """
    Delete record if all relations are False
    """
    DeleteEmptyRelations.delay(sender, instance.id)


@receiver(relation_changed, sender=MovieRelation)
@receiver(relation_changed, sender=PersonRelation)
def recount_familiar_objects(sender, instance, **kwargs):
    """
    Recount familiar movies | persons for user
    """
    RecountFamiliarObjects.delay(sender, instance.user.id)