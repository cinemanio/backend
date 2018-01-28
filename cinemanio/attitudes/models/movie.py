from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import ugettext_lazy as _

from cinemanio.attitudes.models.base import AttitudeBase, register_attitude_fields
from cinemanio.core.models import Movie


class MovieAttitude(AttitudeBase):
    class Meta(AttitudeBase.Meta):
        pass

    object = models.ForeignKey(Movie, related_name='attitudes', on_delete=models.CASCADE)
    fields = (
        ('fav', _('Fav'), _('Faved'), _('faved movie'), _('You faved movie %s')),
        ('like', _('Like'), _('Liked'), _('liked movie'), _('You liked movie %s')),
        ('seen', _('Have watched'), _('Have watched'), _('watched movie'), _('You watched movie %s')),
        ('dislike', _('Dislike'), _('Disliked'), _('disliked movie'), _('You disliked movie %s')),
        ('want', _('Want to watch'), _('Want to watch'), _('want to watch movie'), _('You want to watch movie %s')),
        ('ignore', _('Don\'t want to watch'), _('Don\'t want to watch'), _('don\'t want to watch movie'),
         _('You don\'t want to watch movie %s')),
        ('have', _('Have in collection'), _('Have in collection'), _('got to collection movie'),
         _('You got to collection movie %s')),
    )

    def correct_fields(self, name, value):
        if value is True:
            if name in ('seen', 'like', 'dislike', 'fav'):
                self.want = False
                self.ignore = False
            if name == 'like':
                self.seen = True
                self.dislike = False
            if name == 'dislike':
                self.seen = True
                self.ignore = True
                self.like = False
            if name == 'fav':
                self.like = True
                self.seen = True
            if name == 'want':
                self.ignore = False
            if name == 'ignore':
                self.want = False

        if value is False:
            if name == 'seen':
                self.dislike = False
                self.like = False
                self.fav = False
            if name == 'like':
                self.fav = False


class MovieAttitudeCount(models.Model):
    object = models.OneToOneField(Movie, related_name='attitudes_count', on_delete=models.CASCADE)


get_user_model().add_to_class('familiar_movies', models.ManyToManyField(
    Movie, verbose_name=_('Attitudes'), through=MovieAttitude, related_name='attitudes_users'))

register_attitude_fields(MovieAttitude, MovieAttitudeCount)
