from django.forms.widgets import Widget
from django.utils.html import format_html
from sorl.thumbnail import get_thumbnail

from cinemanio.images.models import Image


class AdminImagePreviewWidget(Widget):
    """
    A FileField Widget for only previewing image
    """

    def render(self, name, value, **_):
        if not value:
            return ''

        thumb = get_thumbnail(value, '{}x{}'.format(*Image.ICON_SIZE)).url

        return format_html('''<input type="hidden" name="{}" value="{}" />
            <a target="_blank" href="{}"><img src="{}" alt="{}" /></a>''', name, value, value.url, thumb, value)
