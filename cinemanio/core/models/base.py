from django.db import models
from django.utils.translation import ugettext_lazy as _


class BaseModel(models.Model):
    """
    Base model for Movie and Person
    """
    slug = models.SlugField(_('Slug'), max_length=100, unique=True, null=True, blank=True)

    site_official_url = models.URLField(_('Official site'), null=True, blank=True)
    site_fan_url = models.URLField(_('Fan site'), null=True, blank=True)

    class Meta:
        abstract = True

    def __str__(self):
        return repr(self)
