import re
from difflib import SequenceMatcher

import wikipedia
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.translation import ugettext_lazy as _
from wikipedia.exceptions import DisambiguationError, PageError

from cinemanio.core.models import Movie, Person
from cinemanio.sites.exceptions import PossibleDuplicate, WrongValue
from cinemanio.sites.models import SitesBaseModel


class WikipediaPageManager(models.Manager):
    movie_term_map = {
        'en': '{title} ({year} film)',
        'ru': '{title} (фильм, {year})',
    }

    person_term_map = {
        'en': '{first_name} {last_name}',
        'ru': '{last_name}, {first_name}',
    }

    stop_words = [
        '(disambiguation)',
        '(значения)',
    ]

    def get_search_term(self, instance, lang) -> str:
        """
        Get search term for Wikipedia search API
        """
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
        return term

    def create_from_list_for(self, instance, lang, links):
        """
        Create WikipediaPage object for instance using list of links from existing Wikipedia page
        """
        term = self.get_search_term(instance, lang)
        for link in links:
            if self.validate_search_result(link, term):
                try:
                    return self.safe_create(link, lang, instance)
                except PossibleDuplicate:
                    continue

        raise ValueError(f"No Wikipedia pages found for {instance._meta.model_name} ID={instance.pk} "
                         f"on language {lang} in the list of links")

    def create_for(self, instance, lang='en'):
        """
        Create WikipediaPage object for instance using Wikipedia search API
        """
        if lang not in self.movie_term_map or lang not in self.person_term_map:
            raise ValueError(f"Value of lang attribute is unknown: {lang}")

        term = self.get_search_term(instance, lang)
        wikipedia.set_lang(lang)
        results = wikipedia.search(term, results=1)
        if results and self.validate_search_result(results[0], term):
            return self.safe_create(results[0], lang, instance)

        raise ValueError(f"No Wikipedia pages found for {instance._meta.model_name} ID={instance.pk} "
                         f"on language {lang} using search term '{term}'")

    def validate_search_result(self, result, term, remove_years=True) -> bool:
        """
        Validate search results:
        - check stop words
        - calculate similarity of search result and search term, removing movie years (depends on remove_years attr)
        (quick solution from here
        https://stackoverflow.com/questions/17388213/find-the-similarity-metric-between-two-strings)
        - compare years of movie and search result using delta
        """
        for stop_word in self.stop_words:
            if stop_word in result:
                return False

        # remove year from the movie search term
        m1 = m2 = None
        if remove_years:
            m1 = re.findall(r'^(.+) \(', result)
            m2 = re.findall(r'^(.+) \(', term)
        if SequenceMatcher(None,
                           m1[0] if m1 else result,
                           m2[0] if m2 else term).ratio() < 0.7:
            return False

        # year comparison
        m1 = re.findall(r'\d{4}', result)
        m2 = re.findall(r'\d{4}', term)
        if m1 and m2 and abs(int(m1[0]) - int(m2[0])) > 1:
            return False

        return True

    def safe_create(self, title, lang, instance):
        """
        Create WikipediaPage object safely, preventing IntegrityError.
        Raise PossibleDublicate and WrongValue exceptions in corresponding cases.
        """
        instance_type = instance._meta.model_name
        try:
            object_exist = self.get(lang=lang, title=title)
            if object_exist.content_object == instance:
                return object_exist
            raise PossibleDuplicate(
                f"Can not assign Wikipedia page title='{title}' lang={lang} to {instance_type} ID={instance.id}, "
                f"because it's already assigned to {instance_type} ID={object_exist.content_object.id}")
        except self.model.DoesNotExist:
            try:
                instance_exist = self.get(lang=lang, **{instance_type: instance})
                if title != instance_exist.title:
                    raise WrongValue(
                        f"Can not assign Wikipedia page title='{title}' lang={lang} to {instance_type} ID={instance.id},"
                        f" because another Wikipedia page title='{instance_exist.title}' already assigned there")
            except self.model.DoesNotExist:
                return self.create(lang=lang, title=title, content_object=instance)


class WikipediaPage(SitesBaseModel):
    """
    Wikipedia model
    """
    lang = models.CharField(_('Language'), max_length=5, db_index=True)
    title = models.CharField(_('Title'), max_length=100, unique=True)
    content = models.TextField(_('Content'), blank='', default='')
    page_id = models.PositiveIntegerField(_('Page ID'), null=True)

    # relation to Movie or Person
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    link = 'http://{lang}.wikipedia.org/wiki/{title}'

    objects = WikipediaPageManager()

    class Meta:
        unique_together = (
            ('lang', 'title'),
            ('content_type', 'object_id', 'lang'),
        )

    @property
    def url(self):
        return self.link.format(title=self.title.replace(' ', '_'), lang=self.lang)

    def sync(self):
        """
        Sync instance using Wikipedia API. Update content, page_id fields
        """
        from cinemanio.sites.wikipedia.signals import wikipedia_page_synced
        wikipedia.set_lang(self.lang)
        try:
            page = wikipedia.page(self.title, auto_suggest=False)
        except PageError:
            self.delete()
        except DisambiguationError as e:
            term = WikipediaPage.objects.get_search_term(self.content_object, self.lang)
            for link in e.options:
                if WikipediaPage.objects.validate_search_result(link, term, remove_years=False):
                    self.title = link
                    self.sync()
        else:
            self.content = page.content
            self.page_id = page.pageid
            wikipedia_page_synced.send(sender=WikipediaPage, page=page, lang=self.lang,
                                       content_type_id=self.content_type_id, object_id=self.object_id)
            super().sync()


Movie.add_to_class('wikipedia', GenericRelation(WikipediaPage, verbose_name=_('Wikipedia'),
                                                related_query_name='movie'))
Person.add_to_class('wikipedia', GenericRelation(WikipediaPage, verbose_name=_('Wikipedia'),
                                                 related_query_name='person'))
