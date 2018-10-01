from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import ugettext_lazy as _

from cinemanio.relations.models.base import RelationBase, register_relation_fields

User = get_user_model()


class UserRelation(RelationBase):
    class Meta(RelationBase.Meta):
        pass

    object = models.ForeignKey(User, related_name="relations", on_delete=models.CASCADE)
    fields = (
        (
            "friend",
            _("Friend"),
            _("Friends"),
            _("started friendship with user"),
            _("You started friendship with user %s"),
        ),
        ("expert", _("Expert"), _("Experts"), _("thought user is an expert"), _("You think user %s is an expert")),
    )

    # def is_backward_attitude(self):
    #     try:
    #         backward_attitude = ProfileAttitude.objects.get(user=self.object, object=self.user)
    #         assert backward_attitude.friend or backward_attitude.expert
    #         return True
    #     except (ProfileAttitude.DoesNotExist, AssertionError):
    #         return False


class UserRelationCount(models.Model):
    object = models.OneToOneField(User, related_name="relations_count", on_delete=models.CASCADE)
    movies = models.PositiveIntegerField(default=0, verbose_name=_("Familiar movies count"))
    persons = models.PositiveIntegerField(default=0, verbose_name=_("Familiar persons count"))


User.add_to_class(
    "familiar_users_back",
    models.ManyToManyField(
        "self", verbose_name=_("Relations"), through=UserRelation, related_name="familiar_users", symmetrical=False
    ),
)

register_relation_fields(UserRelation, UserRelationCount)
