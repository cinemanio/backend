import re
from difflib import SequenceMatcher

import wikipedia
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.translation import ugettext_lazy as _
from wikipedia.exceptions import DisambiguationError, PageError

from cinemanio.core.models import Movie, Person
from cinemanio.sites.exceptions import PossibleDuplicate, WrongValue, NothingFound
from cinemanio.sites.models import SitesBaseModel


class WikipediaPageManager(models.Manager):
    movie_term_map = {"en": "{title} ({year} film)", "ru": "{title} (фильм, {year})"}

    person_term_map = {"en": "{first_name} {last_name}", "ru": "{last_name}, {first_name}"}

    stop_words = ["(disambiguation)", "(значения)"]

    def get_term_for(self, instance, lang) -> str:
        """
        Get search term for Wikipedia search API
        """
        if isinstance(instance, Movie):
            title = getattr(instance, f"title_{lang}")
            if not title:
                raise ValueError("To be able search Wikipedia page movie should has a title")
            term = self.movie_term_map[lang].format(title=title, year=instance.year)
        elif isinstance(instance, Person):
            first_name = getattr(instance, f"first_name_{lang}")
            last_name = getattr(instance, f"last_name_{lang}")
            if not first_name or not last_name:
                raise ValueError("To be able search Wikipedia page person should has first name and last name")
            term = self.person_term_map[lang].format(first_name=first_name, last_name=last_name)
        else:
            raise TypeError(f"Type of instance attribute is unknown: {type(instance)}")
        return term

    def create_from_list_for(self, instance, lang, titles, term=None) -> "WikipediaPage":
        """
        Create WikipediaPage object for instance using list of links (from existing Wikipedia page or search results)
        With years validation comparison first time (more strict) if nothing is found try another time without years
        """
        if term is None:
            term = self.get_term_for(instance, lang)
        try:
            return self._create_from_list_for(instance, lang, titles, term, remove_years=False)
        except NothingFound:
            return self._create_from_list_for(instance, lang, titles, term, remove_years=True)

    def _create_from_list_for(self, instance, lang, titles, term, remove_years) -> "WikipediaPage":
        """
        Create WikipediaPage object for instance with validation of every link. If no link matches raise NothingFound
        """
        for title in titles:
            if self.validate_title(title, term, remove_years=remove_years):
                return self.safe_create(title, lang, instance)

        raise NothingFound(
            f"No Wikipedia page found for {instance._meta.model_name} ID={instance.pk} " f"on language {lang}"
        )

    def create_for(self, instance, lang="en") -> "WikipediaPage":
        """
        Create WikipediaPage object for instance using Wikipedia search API
        """
        if lang not in self.movie_term_map or lang not in self.person_term_map:
            raise ValueError(f"Unknown value of lang attribute: {lang}")

        term = self.get_term_for(instance, lang)
        wikipedia.set_lang(lang)
        results = wikipedia.search(term, results=10)
        return self.create_from_list_for(instance, lang, results, term)

    def validate_title(self, title, term, remove_years=True) -> bool:
        """
        Validate title:
        - check stop words
        - if movie part number is specified in term, ensure it's also in title
        - calculate similarity of title and search term, removing movie years (depends on remove_years attr)
        (quick solution from here
        https://stackoverflow.com/questions/17388213/find-the-similarity-metric-between-two-strings)
        - compare years of movie and search result using delta
        """
        for stop_word in self.stop_words:
            if stop_word in title:
                return False

        # movie part number
        m1 = re.findall(r"( \d+) \(", term)
        if m1:
            remove_years = True
            if m1[0] not in title:
                return False

        # years comparison
        m1 = re.findall(r"\d{4}", title)
        m2 = re.findall(r"\d{4}", term)
        if m1 and m2 and abs(int(m1[0]) - int(m2[0])) > 1:
            return False

        # remove years
        if remove_years:
            title = re.sub(r"^(.+) \(.*\d{4}.*\)", r"\1", title)
            term = re.sub(r"^(.+) \(.*\d{4}.*\)", r"\1", term)

        # similarity check
        if SequenceMatcher(None, title, term).ratio() < 0.7:
            return False

        return True

    def safe_create(self, title, lang, instance) -> "WikipediaPage":
        """
        Create WikipediaPage object safely, preventing IntegrityError.
        Raise PossibleDublicate and WrongValue exceptions in corresponding cases.
        """
        instance_type = instance._meta.model_name
        try:
            wikipedia_page = self.get(lang=lang, title=title)
            if wikipedia_page.content_object != instance:
                raise PossibleDuplicate(
                    f"Can not assign Wikipedia page title='{title}' lang={lang} to {instance_type} ID={instance.id}, "
                    f"because it's already assigned to {instance_type} ID={wikipedia_page.content_object.id}"
                )
        except self.model.DoesNotExist:
            try:
                wikipedia_page = self.get(lang=lang, **{instance_type: instance})
                if title != wikipedia_page.title:
                    raise WrongValue(
                        f"Can not assign Wikipedia page title='{title}' lang={lang} to {instance_type} ID={instance.id},"
                        f" because another Wikipedia page title='{wikipedia_page.title}' already assigned there"
                    )
            except self.model.DoesNotExist:
                wikipedia_page = self.create(lang=lang, title=title, content_object=instance)
        return wikipedia_page


class WikipediaPage(SitesBaseModel):
    """
    Wikipedia model
    """

    lang = models.CharField(_("Language"), max_length=5, db_index=True)
    title = models.CharField(_("Title"), max_length=100, unique=True)
    content = models.TextField(_("Content"), blank="", default="")
    page_id = models.PositiveIntegerField(_("Page ID"), null=True)

    # relation to Movie or Person
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")

    link = "http://{lang}.wikipedia.org/wiki/{title}"

    objects = WikipediaPageManager()

    class Meta:
        unique_together = (("lang", "title"), ("content_type", "object_id", "lang"))

    @property
    def url(self) -> str:
        return self.link.format(title=self.title.replace(" ", "_"), lang=self.lang)

    def sync(self, **_) -> None:
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
            term = WikipediaPage.objects.get_term_for(self.content_object, self.lang)
            for title in e.options:
                if WikipediaPage.objects.validate_title(title, term, remove_years=False):
                    self.title = title
                    self.sync()
        else:
            self.content = page.content
            self.page_id = page.pageid
            wikipedia_page_synced.send(
                sender=WikipediaPage,
                page=page,
                lang=self.lang,
                content_type_id=self.content_type_id,
                object_id=self.object_id,
            )
            super().sync()


Movie.add_to_class("wikipedia", GenericRelation(WikipediaPage, verbose_name=_("Wikipedia"), related_query_name="movie"))
Person.add_to_class(
    "wikipedia", GenericRelation(WikipediaPage, verbose_name=_("Wikipedia"), related_query_name="person")
)
