from django.forms.widgets import Widget
from django.utils.safestring import mark_safe
from sorl.thumbnail import get_thumbnail

from cinemanio.images.models import Image


class AdminImagePreviewWidget(Widget):
    """
    A FileField Widget for only previewing image
    """

    def render(self, name, value, **_):
        output = []
        if value:
            try:  # is image
                # Image.open(os.path.join(settings.MEDIA_ROOT, file_name))
                output.append(
                    """
                    <input type="hidden" name="%s" value="%s" />
                    <a target="_blank" href="%s"><img src="%s" alt="%s" /></a>
                    """
                    % (name, value, value.url, get_thumbnail(value, "{}x{}".format(*Image.ICON_SIZE)).url, value)
                )
            except IOError:  # not image
                output.append('<input type="text" name="%s" />' % name)
        else:
            output.append('<input type="text" name="%s" />' % name)

        return mark_safe("".join(output))
