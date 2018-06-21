from django.contrib import admin
from django.contrib.admin.widgets import ForeignKeyRawIdWidget, NoReverseMatch, reverse, Truncator


class FastForeignKeyRawIdWidget(ForeignKeyRawIdWidget):
    """
    ForeignKeyRawIdWidget, which doesn't make extra hit to DB, when rendered in inline form
    But take prepopulated value from instance
    """
    def __init__(self, *args, **kwargs):
        self.instance = kwargs.pop('instance')
        self.field = kwargs.pop('field')
        super().__init__(admin_site=admin.site, *args, **kwargs)

    def label_and_url_for_value(self, value):
        try:
            obj = getattr(self.instance, self.field)
        except AttributeError:
            return '', ''

        try:
            url = reverse(
                '%s:%s_%s_change' % (
                    self.admin_site.name,
                    obj._meta.app_label,
                    obj._meta.object_name.lower(),
                ),
                args=(obj.pk,)
            )
        except NoReverseMatch:
            url = ''  # Admin not registered for target model.

        return Truncator(obj).words(14, truncate='...'), url
