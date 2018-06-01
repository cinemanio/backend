from enumfields import IntEnum, EnumIntegerField
from django.db import models
from django.db.models import Count
from django.utils.translation import ugettext_lazy as _, get_language

from cinemanio.core.models.base import BaseModel


class Gender(IntEnum):
    FEMALE = 0
    MALE = 1


class Person(BaseModel):
    """
    Person model
    """
    first_name = models.CharField(_('First name'), max_length=50, db_index=True)
    last_name = models.CharField(_('Last name'), max_length=50, db_index=True)

    biography = models.TextField(_('Biography'), blank=True, default='')
    gender = EnumIntegerField(Gender, verbose_name=_('Gender'), null=True, db_index=True)
    date_birth = models.DateField(_('Date of birth'), blank=True, null=True)
    date_death = models.DateField(_('Date of death'), blank=True, null=True)

    roles = models.ManyToManyField('Role', verbose_name=_('Roles'))
    country = models.ForeignKey('Country', verbose_name=_('Country of birth'), blank=True, null=True,
                                on_delete=models.CASCADE)
    movies = models.ManyToManyField('Movie', verbose_name=_('Movies'), through='Cast')

    class Meta:
        verbose_name = _('person')
        verbose_name_plural = _('persons')
        get_latest_by = 'id'

    @property
    def name(self):
        return ' '.join([self.first_name, self.last_name]).strip()

    @property
    def name_en(self):
        return ' '.join([self.first_name_en, self.last_name_en]).strip()

    @property
    def name_ru(self):
        return ' '.join([self.first_name_ru, self.last_name_ru]).strip()

    def __repr__(self):
        names = [self.name]
        if get_language() != 'en' and self.name != self.name_en:
            names += [self.name_en]
        return ', '.join(names)

    def set_roles(self):
        roles = self.career.values('role').annotate(count=Count('role')).order_by('role')
        total = sum([role['count'] for role in roles])
        for role in roles:
            if role['count'] / total > 0.1:
                self.roles.add(role['role'])
