from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import ugettext_lazy as _

from cinemanio.relations.models.base import RelationBase, register_relation_fields
from cinemanio.core.models import Person


class PersonRelation(RelationBase):
    class Meta(RelationBase.Meta):
        pass

    object = models.ForeignKey(Person, related_name="relations", on_delete=models.CASCADE)
    fields = (
        ("fav", _("Fav"), _("Faved"), _("faved person"), _("You faved person %s")),
        ("like", _("Like"), _("Liked"), _("liked person"), _("You liked person %s")),
        ("dislike", _("Dislike"), _("Disliked"), _("disliked person"), _("You disliked person %s")),
    )

    def correct_fields(self, name, value):
        if value is True:
            if name == "like":
                self.dislike = False
            if name == "dislike":
                self.like = False
                self.fav = False
            if name == "fav":
                self.like = True
                self.dislike = False

        if value is False:
            if name == "like":
                self.fav = False


class PersonRelationCount(models.Model):
    object = models.OneToOneField(Person, related_name="relations_count", on_delete=models.CASCADE)


get_user_model().add_to_class(
    "familiar_persons",
    models.ManyToManyField(Person, verbose_name=_("Relations"), through=PersonRelation, related_name="relations_users"),
)

register_relation_fields(PersonRelation, PersonRelationCount)
