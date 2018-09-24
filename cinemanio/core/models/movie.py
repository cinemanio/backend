from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _, get_language

from cinemanio.core.models.base import BaseModel

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


class Movie(BaseModel):
    """
    Movie model
    """
    YEARS_RANGE = (1894, timezone.now().year + 10)
    transliteratable_fields = ['title']

    title = models.CharField(_('Title'), max_length=200, default='')
    title_original = models.CharField(_('Title original'), max_length=200, default='')

    year = models.PositiveSmallIntegerField(_('Year'), null=True, db_index=True,
                                            help_text=_(
                                                'Year in between {} and {}'.format(YEARS_RANGE[0], YEARS_RANGE[1])),
                                            validators=[MinValueValidator(YEARS_RANGE[0]),
                                                        MaxValueValidator(YEARS_RANGE[1])])
    runtime = models.SmallIntegerField(_('Runtime in minutes'), blank=True, null=True)

    award = models.IntegerField(_('Main award'), choices=AWARD_CHOICES, blank=True, null=True)

    genres = models.ManyToManyField('Genre', verbose_name=_('Genres'), related_name='movies', blank=True)
    languages = models.ManyToManyField('Language', verbose_name=_('Languages'), related_name='movies', blank=True)
    countries = models.ManyToManyField('Country', verbose_name=_('Countries'), related_name='movies', blank=True)
    persons = models.ManyToManyField('Person', verbose_name=_('Persons'), through='Cast')

    sequel_for = models.ForeignKey('Movie', verbose_name=_('Sequel for movie'), related_name='prequels', blank=True,
                                   null=True, on_delete=models.CASCADE)
    prequel_for = models.ForeignKey('Movie', verbose_name=_('Prequel for movie'), related_name='sequels', blank=True,
                                    null=True, on_delete=models.CASCADE)
    remake_for = models.ForeignKey('Movie', verbose_name=_('Remake of movie'), related_name='remakes', blank=True,
                                   null=True, on_delete=models.CASCADE)
    novel_isbn = models.IntegerField(_('ISBN'), blank=True, null=True)

    class Meta:
        verbose_name = _('movie')
        verbose_name_plural = _('movies')

    def __repr__(self):
        info = []
        if get_language() != 'en' and self.title != self.title_en:
            info += [self.title_en]
        info += [str(self.year)]
        return '{title} ({info})'.format(title=self.title, info=', '.join(info))
