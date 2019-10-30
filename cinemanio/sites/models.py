from datetime import timedelta
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.conf import settings

from cinemanio.core.models.movie import Movie, MovieQuerySet
from cinemanio.core.models.person import Person, PersonQuerySet


class SitesBaseModel(models.Model):
    synced_at = models.DateTimeField(_('Synced at'), null=True, db_index=True)

    class Meta:
        abstract = True

    def sync(self, **_) -> None:
        self.synced_at = timezone.now()


def get_sites_queryset(queryset):
    class SitesQuerySet(queryset):
        def without_site(self, site, lang=None):
            if site == 'wikipedia':
                return self.exclude(wikipedia__lang=lang)
            else:
                return self.filter(**{site: None})

        def with_site(self, site, lang=None):
            if site == 'wikipedia':
                return self.filter(wikipedia__lang=lang)
            else:
                return self.exclude(**{site: None})

        def with_site_uptodate(self, site, lang=None):
            if site == 'wikipedia':
                return self.filter(wikipedia__lang=lang, wikipedia__synced_at__gte=self.get_expiration_date())
            else:
                return self.filter(**{f'{site}__synced_at__gte': self.get_expiration_date()})

        def with_site_outdated(self, site, lang=None):
            if site == 'wikipedia':
                return self.filter(wikipedia__lang=lang, wikipedia__synced_at__lt=self.get_expiration_date())
            else:
                return self.filter(**{f'{site}__synced_at__lt': self.get_expiration_date()})

        def get_expiration_date(self):
            return timezone.now() - timedelta(days=getattr(settings, 'SITES_EXPIRATION_DAYS', 31))

    return SitesQuerySet


Movie.add_to_class('sites', get_sites_queryset(MovieQuerySet).as_manager())
Person.add_to_class('sites', get_sites_queryset(PersonQuerySet).as_manager())
