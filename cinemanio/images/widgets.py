from django.forms.widgets import Widget
from django.utils.safestring import mark_safe
from sorl.thumbnail import get_thumbnail

from cinemanio.images.models import Image


class AdminImagePreviewWidget(Widget):
    """
    A FileField Widget for only previewing image
    """

    def render(self, name, value, **_):
        if value:
            try:
                # is image
                thumb = get_thumbnail(value, '{}x{}'.format(*Image.ICON_SIZE)).url
                output = f'''<input type="hidden" name="{name}" value="{value}" />
                    <a target="_blank" href="{value.url}"><img src="{thumb}" alt="{value}" /></a>'''
            except IOError:  # not image
                output = f'<input type="text" name="{name}" />'
        else:
            output = f'<input type="text" name="name" />'

        return mark_safe(output)
