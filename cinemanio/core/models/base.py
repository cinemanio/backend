from django.db import models
from django.utils.translation import ugettext_lazy as _
from transliterate import translit
from transliterate.base import registry

from cinemanio.core.translit.ru import RussianLanguagePack

registry.register(RussianLanguagePack)


class BaseModel(models.Model):
    """
    Base model for Movie and Person
    """

    slug = models.SlugField(_("Slug"), max_length=100, unique=True, null=True, blank=True)

    site_official_url = models.URLField(_("Official site"), null=True, blank=True)
    site_fan_url = models.URLField(_("Fan site"), null=True, blank=True)

    class Meta:
        abstract = True

    def __str__(self):
        return repr(self)

    @property
    def transliteratable_fields(self):
        raise NotImplementedError()

    def set_transliteratable_fields(self):
        """
        If some fields non-specified in English, but specified in other language -
        assign transliteratable version for the English and main field
        """
        for lang in ["ru"]:
            for field in self.transliteratable_fields:
                field_lang = "{}_{}".format(field, lang)
                field_en = "{}_{}".format(field, "en")
                value_lang = getattr(self, field_lang)
                value_en = getattr(self, field_en)
                value = getattr(self, field)
                if value_lang:
                    if not value or not value_en:
                        value_translit = translit(value_lang, lang, reversed=True)
                        if not value:
                            setattr(self, field, value_translit)
                        if not value_en:
                            setattr(self, field_en, value_translit)
