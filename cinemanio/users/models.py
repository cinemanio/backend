from django.contrib.auth.models import UserManager, AbstractUser
from django.db import models
from django.utils.translation import ugettext_lazy as _

from cinemanio.core.models import Gender


class User(AbstractUser):
    """
    User model
    """
    # avatar = ImageField(upload_to=provile_avatar_upload_to, verbose_name=_('Avatar'), null=True, blank=True,
    #                     help_text=_('By default we search your avatar on <a href="http://ru.gravatar.com">Gravatar</a>'
    #                                 ' service using your email address, and also you can upload image into this field.'
    #                                 ' We accept jpeg, gif and png formats.'))

    date_birth = models.DateField(_('Date of birth'), blank=True, null=True)
    gender = models.IntegerField(_('Gender'), choices=Gender.choices(), blank=True, null=True,
                                 db_index=True)

    icq = models.PositiveIntegerField(_('ICQ'), blank=True, null=True)
    jabber = models.CharField(_('Jabber'), blank=True, max_length=50)
    gtalk = models.CharField(_('Google Talk'), blank=True, max_length=50, default='')
    googleprofile = models.CharField(_('Google Profile'), blank=True, max_length=50, default='')
    skype = models.CharField(_('Skype'), blank=True, max_length=50)
    msn = models.CharField(_('Messenger'), blank=True, max_length=50)
    lj = models.CharField(_('Livejournal'), blank=True, null=True, max_length=50, unique=True)
    site = models.URLField(_('Homepage'), blank=True)

    about = models.TextField(_('About myself'), blank=True)
    city = models.CharField(_('City'), blank=True, max_length=50)
    genres = models.ManyToManyField('core.Genre', verbose_name=_('Favorite genres'), related_name='users', blank=True)

    # Use UserManager to get the create_user method, etc.
    # objects = ModelQuerySetManager(UserManager)
    objects = UserManager()

    livejournal_link = 'http://%s.livejournal.com/'
    googleprofile_link = 'http://www.google.com/profiles/%s'

    class Meta(AbstractUser.Meta):
        verbose_name = _('user')
        verbose_name_plural = _('users')
        ordering = ('username',)

    @property
    def googleprofile_url(self):
        return self.googleprofile_link % self.googleprofile if self.googleprofile else ''

    def __repr__(self):
        return self.username

    @property
    def name(self):
        name = self.first_name + ' ' + self.last_name
        return name.strip()
