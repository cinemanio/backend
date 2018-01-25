from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from cinemanio.core.models.base import BaseModel
# from cinemanio.core.models import Role
# from cinemanio.core.fields import ForeignCountField

AWARD_CHOICES = (
    (1773, 'Берлинский кинофестиваль'),
    (8298, 'Венецианский кинофестиваль'),
    (8296, 'Европейская кинопремия'),
    (1762, 'Золотой глобус'),
    (1766, 'Золотой орел'),
    (1783, 'Золотой Остап'),
    (1768, 'Каннский кинофестиваль'),
    (1769, 'Кинопремия Британской киноакадемии'),
    (1781, 'Кинопремия Международной ассоциации анимационного кино'),
    (1763, 'Кинопремия телеканала MTV'),
    (1767, 'Кинотавр'),
    (9395, 'Киношок'),
    (1784, 'Кумир'),
    (1770, 'Медный всадник'),
    (8297, 'Московский международный кинофестиваль'),
    (1765, 'Ника'),
    (152, 'Оскар'),
    (1772, 'Сатурн'),
    (1771, 'Сезар'),
    (1764, 'Эмми'),
)

YEAR_CHOICES = [(year, year) for year in range(timezone.now().year + 10, 1894, -1)]


class Movie(BaseModel):
    """
    Movie model
    """
    title = models.CharField(_('Title'), max_length=200, default='')

    year = models.SmallIntegerField(_('Year'), choices=YEAR_CHOICES, null=True, db_index=True)
    runtime = models.SmallIntegerField(_('Runtime in minutes'), blank=True, null=True)

    award = models.IntegerField(_('Main award'), choices=AWARD_CHOICES, blank=True, null=True)

    types = models.ManyToManyField('Type', verbose_name=_('Movie types'), related_name='movies', blank=True)
    genres = models.ManyToManyField('Genre', verbose_name=_('Genres'), related_name='movies', blank=True)
    languages = models.ManyToManyField('Language', verbose_name=_('Languages'), related_name='movies', blank=True)
    countries = models.ManyToManyField('Country', verbose_name=_('Countries'), related_name='movies', blank=True)
    persons = models.ManyToManyField('Person', verbose_name=_('Persons'), through='Cast')

    # persons_count = ForeignCountField(Role, 'movie', 'persons', verbose_name=_('Persons count'), distinct=True)

    sequel_for = models.ForeignKey('self', verbose_name=_('Sequel for movie'), related_name='prequels', blank=True,
                                   null=True, on_delete=models.CASCADE)
    prequel_for = models.ForeignKey('self', verbose_name=_('Prequel for movie'), related_name='sequels', blank=True,
                                    null=True, on_delete=models.CASCADE)
    remake_for = models.ForeignKey('self', verbose_name=_('Remake of movie'), related_name='remakes', blank=True,
                                   null=True, on_delete=models.CASCADE)
    novel_isbn = models.IntegerField(_('ISBN'), blank=True, null=True)

    class Meta:
        verbose_name = _('movie')
        verbose_name_plural = _('movies')

    def __repr__(self):
        return '{title} ({year})'.format(title=self.title, year=self.year)
