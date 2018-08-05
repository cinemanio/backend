import re
from difflib import SequenceMatcher

import wikipedia
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.translation import ugettext_lazy as _
from wikipedia.exceptions import DisambiguationError, PageError

from cinemanio.core.models import Movie, Person
from cinemanio.sites.exceptions import PossibleDuplicate
from cinemanio.sites.models import SitesBaseModel
from cinemanio.sites.wikipedia.signals import wikipedia_page_synced


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
            title = getattr(instance, f'title_{lang}')
            if not title:
                raise ValueError("To be able search Wikipedia page movie should has a title")
            term = self.movie_term_map[lang].format(title=title, year=instance.year)
        elif isinstance(instance, Person):
            first_name = getattr(instance, f'first_name_{lang}')
            last_name = getattr(instance, f'last_name_{lang}')
            if not first_name or not last_name:
                raise ValueError("To be able search Wikipedia page person should has first name and last name")
            term = self.person_term_map[lang].format(first_name=first_name, last_name=last_name)
        else:
            raise TypeError(f"Type of instance attribute is unknown: {type(instance)}")

        wikipedia.set_lang(lang)
        results = wikipedia.search(term, results=1)
        if self.validate_search_results(results, term):
            page = self.safe_create(results[0], lang, instance)
            page.sync()
            page.save()
            return page

        raise ValueError(f"No Wikipedia pages found for {instance._meta.model_name} ID={instance.pk} "
                         f"on language {lang} using search term '{term}'")

    def validate_search_results(self, results, term) -> bool:
        """
        Validate search results:
        - check length
        - calculate similarity of search result and search term (quick solution from here
        https://stackoverflow.com/questions/17388213/find-the-similarity-metric-between-two-strings)
        - compare years of movie and search result using delta
        """
        if not results:
            return False

        if 'disambiguation' in results[0]:
            return False

        # remove year from the movie search term
        m1 = re.findall(r'^(.+) \(', results[0])
        m2 = re.findall(r'^(.+) \(', term)
        if SequenceMatcher(None,
                           m1[0] if m1 else results[0],
                           m2[0] if m2 else term).ratio() < 0.7:
            return False

        # year comparison
        m1 = re.findall(r'\d{4}', results[0])
        m2 = re.findall(r'\d{4}', term)
        if m1 and m2 and abs(int(m1[0]) - int(m2[0])) > 1:
            return False

        return True

    def safe_create(self, name, lang, instance):
        instance_type = instance._meta.model_name
        try:
            object_exist = self.get(lang=lang, name=name)
            raise PossibleDuplicate(
                f"Can not assign Wikipedia page title='{name}' lang={lang} to {instance_type} ID={instance.id}, "
                f"because it's already assigned to {instance_type} ID={object_exist.content_object.id}")
        except self.model.DoesNotExist:
            return self.create(lang=lang, name=name, content_object=instance)


class WikipediaPage(SitesBaseModel):
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
        unique_together = (
            ('lang', 'name'),
            ('content_type', 'object_id', 'lang'),
        )

    @property
    def url(self):
        return self.link.format(name=self.name.replace(' ', '_'), lang=self.lang)

    def sync(self):
        wikipedia.set_lang(self.lang)
        try:
            page = wikipedia.page(self.name)
        except (DisambiguationError, PageError):
            self.delete()
        else:
            self.content = page.content
            wikipedia_page_synced.send(sender=WikipediaPage, page=page,
                                       content_type_id=self.content_type_id, object_id=self.object_id)
            super().sync()


Movie.add_to_class('wikipedia', GenericRelation(WikipediaPage, verbose_name=_('Wikipedia')))
Person.add_to_class('wikipedia', GenericRelation(WikipediaPage, verbose_name=_('Wikipedia')))
