from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _


class SitesBaseModel(models.Model):
    synced_at = models.DateTimeField(_("Synced at"), null=True, db_index=True)

    class Meta:
        abstract = True

    def sync(self, **_) -> None:
        self.synced_at = timezone.now()
