from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import ugettext_lazy as _

User = get_user_model()


class AttitudeBase(models.Model):
    """
    Base model for all attitudes models
    """

    class Meta:
        unique_together = ('object', 'user')
        ordering = ('id',)
        abstract = True

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    # def __unicode__(self):
    #     return ' | '.join([self.object.__unicode__(), self.user.__unicode__(), \
    #                        ', '.join([tuple[0] + '=' + str(getattr(self, tuple[0])) for tuple in self.fields])])

    def __setattr__(self, name, value):
        """
        Call on every model property change. If change `object`, define `object_id`
        """
        model = self._meta.get_field('object').related_model
        if name == 'object' and not isinstance(value, model):
            name = 'object_id'
            try:
                value = int(value)
            except:
                raise TypeError(_('Field "object" must be integer or %s' % type(model)))
        self.correct_fields(name, value)
        super().__setattr__(name, value)

    def correct_fields(self, name, value):
        """Additional logic between attitude fields"""
        pass

    @property
    def codes(self):
        return [tuple[0] for tuple in self.fields]

    @classmethod
    def get_fieldname_list(cls, number):
        return [(names[0], names[number]) for names in cls.fields]

    @classmethod
    def get_codename_fields(cls):
        return cls.get_fieldname_list(1)

    # @classmethod
    # def get_pastname_fields(cls):
    #     return cls.get_fieldname_list(2)

    # @classmethod
    # def get_fieldname(cls, type, code):
    #     """
    #     Return formcase name of field with defined type and code
    #     """
    #     types = {
    #         'action': 3,
    #         'notification': 4,
    #         'notification_from_user': 5,
    #     }
    #     for field_code, action in cls.get_fieldname_list(types.get(type, 0)):
    #         if code == field_code:
    #             return str(action)
    #
    #     raise ValueError('There is no such field name  of type=%s and code=%s' % (type, code))

    # def save(self, **kwargs):
    #     u"""При сохранении пересчитываем кол-ва отдельных отношений и общее кол-во отношений объекта"""
    #     super(AttitudeBase, self).save(**kwargs)
    #
    #     table_name = self.__class__.__name__.lower()
    #     for code, name in self.get_codename_fields():
    #         setattr(self.object, '%ss_count' % code,
    #                 self.object.attitudes_users.filter(**{'%s__%s' % (table_name, code): True}).count())
    #     setattr(self.object, 'attitudes_count', sum([getattr(self.object, '%ss_count' % code) for code in self.codes]))
    #     self.object.save()

    # def change(self, att_code):
    #     if att_code in self.codes:
    #         setattr(self, att_code, bool(1 - getattr(self, att_code)))

    # def get_most_important(self):
    #     u"""
    #     Выбирает самое значимое отношение из всех возможных
    #     """
    #     for code in ['fav', 'like', 'dislike', 'seen', 'ignore', 'want', 'have', 'expert', 'friend']:
    #         try:
    #             if getattr(self, code) == True:
    #                 return code
    #         except:
    #             pass
    #     return False


def register_attitude_fields(attitude_model, attitude_count_model):
    for code, name in attitude_model.get_codename_fields():
        attitude_model.add_to_class(code, models.BooleanField(verbose_name=name, default=False, db_index=True))
        attitude_count_model.add_to_class('%ss_count' % code, models.PositiveIntegerField(default=0, db_index=True))
