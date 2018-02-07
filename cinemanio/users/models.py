from django.contrib.auth.models import UserManager, AbstractUser
from django.db import models
from django.utils.translation import ugettext_lazy as _


class User(AbstractUser):
    """
    User model
    """
    # avatar = ImageField(upload_to=provile_avatar_upload_to, verbose_name=_('Avatar'), null=True, blank=True,
    #                     help_text=_('By default we search your avatar on <a href="http://ru.gravatar.com">Gravatar</a>'
    #                                 ' service using your email address, and also you can upload image into this field.'
    #                                 ' We accept jpeg, gif and png formats.'))

    date_birth = models.DateField(_('Date of birth'), blank=True, null=True)
    gender = models.IntegerField(_('Gender'), choices=((1, _('Boy')), (0, _('Girl'))), blank=True, null=True,
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

    # notification checkboxes
    email_about_answers = models.BooleanField(_('New answers'), help_text=_(
        'Allow send notifications with new answers for your comments'), default=True)
    email_about_comments = models.BooleanField(_('New comments'), help_text=_(
        'Allow send notifications with new comments for your texts or lists'), default=True)
    email_about_listlinks = models.BooleanField(_('New object in lists'), help_text=_(
        'Allow send notifications about new objects in your lists'), default=True)
    email_super_listlinks = models.BooleanField(_('New object in favorite lists'), help_text=_(
        'Allow send notifications about new objects in your favorite lists'), default=True)
    email_super_objects_comments = models.BooleanField(_('Favorite object comments'), help_text=_(
        'Allow send notifications about new comments of texts or lists you marked as "super"'), default=True,
                                                       db_index=True)
    email_super_objects_changes = models.BooleanField(_('Favorite object changes'), help_text=_(
        'Allow send notifications about changes of any objects you marked as "super"'), default=True, db_index=True)

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

    def __unicode__(self):
        return self.username

    def save(self, **kwargs):
        self.lj = self.lj or None
        super(User, self).save(**kwargs)

    @property
    def name(self):
        name = self.first_name + ' ' + self.last_name
        return name.strip()

    # @property
    # def userpic(self):
    #     imagefile = '/static' + ('/i/avatar_female.png' if self.sex == 0 else '/i/avatar_male.png')
    #
    #     if self.avatar:
    #         imagefile = settings.MEDIA_URL + get_thumbnail(self.avatar, '32x32').name
    #     elif self.email:
    #         imagefile = get_gravatar_url(self.email, size=32)
    #
    #     return imagefile

    # @property
    # def status_class(self):
    #     classes = {
    #         5: 'admin',
    #         4: 'best',
    #         3: 'moder',
    #         2: 'mover2',
    #         1: 'mover1',
    #     }
    #
    #     if self.status in classes.keys():
    #         return classes[self.status]
    #     else:
    #         return ''

    @property
    # @memoize
    def is_editor(self):
        return self.groups.filter(pk=1).count() > 0

    @property
    # @memoize
    def is_moderator(self):
        return self.groups.filter(pk__in=[1, 2]).count() > 0

    @property
    # @memoize
    def is_translator(self):
        return self.groups.filter(pk=3).count() > 0

    # def has_recommendations(self):
    #     try:
    #         assert self.relations
    #         return True
    #     except (AssertionError, ObjectDoesNotExist):
    #         return False
    #
    # def is_enough_persons_for_recommendation(self):
    #     return self.persons_count >= getattr(settings, 'MOVISTER_RECOMMENDATION_ATTITUDES_MIN').get('persons')
    #
    # def is_enough_lists_for_recommendation(self):
    #     return self.attitudes_lists_count >= getattr(settings, 'MOVISTER_RECOMMENDATION_ATTITUDES_MIN').get('lists')
    #
    # def is_enough_genres_for_recommendation(self):
    #     return self.genres.count() >= getattr(settings, 'MOVISTER_RECOMMENDATION_ATTITUDES_MIN').get('genres')
    #
    # def is_enough_types_for_recommendation(self):
    #     return self.types.count() >= getattr(settings, 'MOVISTER_RECOMMENDATION_ATTITUDES_MIN').get('types')
    #
    # def is_enough_all_for_recommendation(self):
    #     return self.is_enough_persons_for_recommendation() \
    #            and self.is_enough_lists_for_recommendation() \
    #            and self.is_enough_genres_for_recommendation() \
    #            and self.is_enough_types_for_recommendation()
    #
    # def set_status(self):
    #     if self.is_editor:
    #         self.status = 5
    #     elif 0:
    #         self.status = 4
    #     elif self.is_moderator:
    #         self.status = 3
    #     elif 0:
    #         self.status = 2
    #     else:
    #         self.status = 1

    # @property
    # def card_movies(self):
    #     return self.attitudes_movies.filter(**{'attitudes__super': True}).order_by('supers_count', 'likes_count')[:5]
    #
    # @property
    # def card_persons(self):
    #     return self.attitudes_persons.filter(**{'attitudes__super': True}).order_by('supers_count', 'likes_count')[:5]

    # @property
    # def related_profile_attitudes(self):
    #     from movister.relations.models import Profile_Attitudes
    #
    #     return Profile_Attitudes.objects.filter(user=self)

    # def friends_experts(self):
    #     return [pa.object for pa in self.related_profile_attitudes.filter(friend=True, expert=True)]
    #
    # def friends(self, only=False):
    #     attitudes = self.related_profile_attitudes.filter(friend=True)
    #     if only:
    #         attitudes = attitudes.filter(expert=False)
    #     return [pa.object for pa in attitudes]
    #
    # def experts(self, only=False):
    #     attitudes = self.related_profile_attitudes.filter(expert=True)
    #     if only:
    #         attitudes = attitudes.filter(friend=False)
    #     return [pa.object for pa in attitudes]

# Profile._meta.get_field('email')._unique = True
