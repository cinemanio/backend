from django.db import models
from django.utils.translation import ugettext_lazy as _


class Cast(models.Model):
    """
    Cast model, connection between Movie and Person
    """

    person = models.ForeignKey('Person', verbose_name=_('Person'), related_name='career', on_delete=models.CASCADE)
    movie = models.ForeignKey('Movie', verbose_name=_('Movie'), related_name='cast', on_delete=models.CASCADE)
    role = models.ForeignKey('Role', verbose_name=_('Role'), related_name='roles', on_delete=models.CASCADE)
    name = models.CharField(_('Role name'), max_length=300, blank=True, default='')

    class Meta:
        verbose_name = _('cast')
        verbose_name_plural = _('cast')
        ordering = ('role', 'id')
        unique_together = ('person', 'movie', 'role')
        get_latest_by = 'id'

    def __repr__(self):
        role = self.role.name.lower()
        if self.role:
            role += ': ' + self.name
        return '{title} - {name} ({role})'.format(
            title=self.movie.title,
            name=self.person.name,
            role=role)

    def save(self, **kwargs):
        from cinemanio.core.models import Role
        if self.role.id not in [Role.ACTOR_ID, Role.ACTOR_VOICE_ID]:
            self.name = ''
        super().save(**kwargs)
