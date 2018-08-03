import wikipedia
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.translation import ugettext_lazy as _

from cinemanio.core.models import Movie, Person
from cinemanio.sites.exceptions import PossibleDuplicate


class WikipediaPageManager(models.Manager):
    movie_term_map = {
        'en': '{title} ({year} film)',
        'ru': '{title} (фильм, {year})',
    }

    person_term_map = {
        'en': '{first_name} {last_name}',
        'ru': '{last_name}, {first_name}',
    }

    def create_for(self, instance, lang='en'):
        if lang not in self.movie_term_map or lang not in self.person_term_map:
            raise ValueError(f"Value of lang attribute is unknown: {lang}")

        if isinstance(instance, Movie):
            term = self.movie_term_map[lang].format(title=getattr(instance, f'title_{lang}'), year=instance.year)
        elif isinstance(instance, Person):
            term = self.person_term_map[lang].format(first_name=getattr(instance, f'first_name_{lang}'),
                                                     last_name=getattr(instance, f'last_name_{lang}'))
        else:
            raise TypeError(f"Type of instance attribute is unknown: {type(instance)}")

        wikipedia.set_lang(lang)
        results = wikipedia.search(term, results=1)
        if len(results):
            page = self.safe_create(content_object=instance, lang=lang, name=results[0])
            page.sync()
            page.save()
            return page

        raise ValueError(f"No Wikipedia pages found for {instance._meta.model_name} ID={instance.pk} "
                         f"on language {lang} using search term '{term}'")

    def safe_create(self, name, lang, content_object):
        try:
            object_exist = self.get(lang=lang, name=name)
            raise PossibleDuplicate(
                f"Can not assign wikipedia page title={name} lang={lang} to {content_object._meta.model_name} ID={content_object.id}, "
                f"because it's already assigned to ID={object_exist.content_object.id}")
        except self.model.DoesNotExist:
            return self.create(lang=lang, name=name, content_object=content_object)


class WikipediaPage(models.Model):
    """
    Wikipedia model
    """
    name = models.CharField(_('Page ID'), max_length=100, unique=True)
    lang = models.CharField(_('Language'), max_length=5, db_index=True)
    content = models.TextField(_('Content'), blank='', default='')

    # relation to Movie or Person
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    link = 'http://{lang}.wikipedia.org/wiki/{name}'

    objects = WikipediaPageManager()

    class Meta:
        unique_together = ('lang', 'name')

    @property
    def url(self):
        return self.link.format(name=self.name, lang=self.lang)

    def sync(self):
        wikipedia.set_lang(self.lang)
        page = wikipedia.page(self.name)
        self.content = page.content


Movie.add_to_class('wikipedia', GenericRelation(WikipediaPage, verbose_name=_('Wikipedia')))
Person.add_to_class('wikipedia', GenericRelation(WikipediaPage, verbose_name=_('Wikipedia')))
