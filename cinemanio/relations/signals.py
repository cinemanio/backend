from django.dispatch import Signal, receiver
from django.contrib.contenttypes.models import ContentType

from cinemanio.relations.models import MovieRelation, PersonRelation, UserRelation
from cinemanio.relations.tasks import recount_familiar_objects, delete_empty_relations, recount_object_relations

relation_changed = Signal(providing_args=["instance", "code", "request"])


@receiver(relation_changed, sender=MovieRelation)
@receiver(relation_changed, sender=PersonRelation)
@receiver(relation_changed, sender=UserRelation)
def delete_empty_relations_signal(sender, instance, **_):
    """
    Delay removing empty relation (all False)
    """
    content_type = ContentType.objects.get_for_model(sender)
    delete_empty_relations.delay(content_type.id, instance.id)


@receiver(relation_changed, sender=MovieRelation)
@receiver(relation_changed, sender=PersonRelation)
def recount_familiar_objects_signal(sender, instance, **_):
    """
    Delay recount of user familiar objects
    """
    content_type = ContentType.objects.get_for_model(sender)
    recount_familiar_objects.delay(content_type.id, instance.user.id)


@receiver(relation_changed, sender=MovieRelation)
@receiver(relation_changed, sender=PersonRelation)
def recount_relations_signal(sender, instance, **_):
    """
    Run recount_object_relations synchronously to provide immediate counts in response
    """
    content_type = ContentType.objects.get_for_model(sender)
    recount_object_relations(content_type.id, instance.id)
