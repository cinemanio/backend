from django.db import models
from django.utils.translation import ugettext_lazy as _

from cinemanio.core.models.person import ACTOR_ID, ACTOR_VOICE_ID


class Cast(models.Model):
    """
    Role model, connection between Movie and Person
    """
    # __metaclass__ = TransMeta

    person = models.ForeignKey('Person', verbose_name=_('Person'), related_name='career', on_delete=models.CASCADE)
    movie = models.ForeignKey('Movie', verbose_name=_('Movie'), related_name='cast', on_delete=models.CASCADE)
    role = models.ForeignKey('Role', verbose_name=_('Amplua'), related_name='roles', on_delete=models.CASCADE)
    name = models.CharField(_('Role name'), max_length=300, blank=True, null=False, default='')

    objects = models.Manager()

    class Meta:
        verbose_name = _('cast')
        verbose_name_plural = _('cast')
        ordering = ('role', 'id')
        unique_together = ('person', 'movie', 'role')
        get_latest_by = 'id'
        # translate = ('role',)

    def __unicode__(self):
        role = self.role.name.lower()
        if self.role:
            role += ': ' + self.name
        return self.movie.title + ' - ' + self.person.name + ' (' + role + ')'

    def save(self, **kwargs):
        if self.role.id not in [ACTOR_ID, ACTOR_VOICE_ID]:
            self.role_ru = ''
            self.role_en = ''
        super(Cast, self).save(**kwargs)
