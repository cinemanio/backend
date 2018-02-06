from django.db import models
from django.utils.translation import ugettext_lazy as _, get_language

from cinemanio.core.models.base import BaseModel


class Person(BaseModel):
    """
    Person model
    """
    first_name = models.CharField(_('First name'), max_length=50, db_index=True)
    last_name = models.CharField(_('Last name'), max_length=50, db_index=True)

    biography = models.TextField(_('Biography'), blank=True, default='')
    gender = models.IntegerField(_('Gender'), choices=((1, _('Male')), (0, _('Female'))), blank=True, null=True,
                                 db_index=True)
    date_birth = models.DateField(_('Date of birth'), blank=True, null=True)
    date_death = models.DateField(_('Date of death'), blank=True, null=True)

    country = models.ForeignKey('Country', verbose_name=_('Country of birth'), blank=True, null=True,
                                on_delete=models.CASCADE)
    movies = models.ManyToManyField('Movie', verbose_name=_('Movies'), through='Cast')

    class Meta:
        verbose_name = _('person')
        verbose_name_plural = _('persons')
        get_latest_by = 'id'

    @property
    def full_name(self):
        return ' '.join([self.first_name, self.last_name]).strip()

    @property
    def full_name_en(self):
        return ' '.join([self.first_name_en, self.last_name_en]).strip()

    def __repr__(self):
        names = [self.full_name]
        if get_language() != 'en' and self.full_name != self.full_name_en:
            names += [self.full_name_en]
        return ', '.join(names)
