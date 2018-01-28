from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.translation import ugettext_lazy as _

from cinemanio.core.models import Movie, Person


class WikipediaPage(models.Model):
    """
    Wikipedia model
    """
    name = models.CharField(_('Page ID'), max_length=100, unique=True)
    lang = models.CharField(_('Language'), max_length=5, db_index=True)

    # relation to Movie or Person
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    link = 'http://{lang}.wikipedia.org/wiki/{name}'

    class Meta:
        unique_together = ('lang', 'name')

    @property
    def url(self):
        return self.link.format(name=self.name, lang=self.lang)

Movie.add_to_class('wikipedia', GenericRelation(WikipediaPage, verbose_name=_('Wikipedia')))
Person.add_to_class('wikipedia', GenericRelation(WikipediaPage, verbose_name=_('Wikipedia')))
