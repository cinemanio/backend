from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _


class SitesBaseModel(models.Model):
    synced_at = models.DateTimeField(_('Synced at'), null=True, db_index=True)

    class Meta:
        abstract = True

    def sync(self, **_):
        self.synced_at = timezone.now()

# In [2]: WikipediaPage.objects.count()
# Out[2]: 0
#
# In [3]: ImdbMovie.objects.count()
# Out[3]: 594
#
# In [4]: ImdbPerson.objects.count()
# Out[4]: 317
#
# In [5]: KinopoiskMovie.objects.count()
# Out[5]: 291
#
# In [6]: KinopoiskPerson.objects.count()
# Out[6]: 0
