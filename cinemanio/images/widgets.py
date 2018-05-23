from django.forms.widgets import Widget
from django.utils.safestring import mark_safe
from django.contrib.admin.widgets import ForeignKeyRawIdWidget
from sorl.thumbnail import get_thumbnail

from cinemanio.images.models import Image


class AdminImagePreviewWidget(Widget):
    """
    A FileField Widget for only previewing image
    """
    def render(self, name, value, *args, **kwargs):
        output = []
        if value:
            try:  # is image
                # Image.open(os.path.join(settings.MEDIA_ROOT, file_name))
                output.append("""
                    <input type="hidden" name="%s" value="%s" />
                    <a target="_blank" href="%s"><img src="%s" alt="%s" /></a>
                    """ % (name, value, value.url, get_thumbnail(value, '{}x{}'.format(*Image.ICON_SIZE)).url, value))
            except IOError:  # not image
                output.append('<input type="text" name="%s" />' % name)
        else:
            output.append('<input type="text" name="%s" />' % name)

        return mark_safe(u''.join(output))


class ForeignKeyRawIdWidget1(ForeignKeyRawIdWidget):
    def label_and_url_for_value(self, value):
        return '', ''
        key = self.rel.get_related_field().name
        try:
            obj = self.rel.model._default_manager.using(self.db).get(**{key: value})
        except (ValueError, self.rel.model.DoesNotExist, ValidationError):
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
