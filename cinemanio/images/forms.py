from django import forms
from django.utils.translation import ugettext_lazy as _

from cinemanio.core.admin.widgets import FastForeignKeyRawIdWidget
from cinemanio.images.widgets import AdminImagePreviewWidget
from cinemanio.images.models import Image, ImageType, ImageSourceType


class ImageInlineForm(forms.ModelForm):
    original = forms.CharField(label=_("Preview"), required=False, widget=AdminImagePreviewWidget)
    type = forms.ChoiceField(label=_("Type"), required=True, choices=[("", _("Select"))] + list(ImageType.choices()))
    source = forms.CharField(label=_("Source"), required=False, max_length=100)
    source_type = forms.ChoiceField(
        label=_("Source Type"), required=False, choices=[("", _("Select"))] + list(ImageSourceType.choices())
    )
    source_id = forms.CharField(label=_("Source Id"), required=False, max_length=100)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["image"].widget = FastForeignKeyRawIdWidget(
            self._meta.model._meta.get_field("image").remote_field, instance=self.instance, field="image"
        )
        try:
            image = self.instance.image
        except Image.DoesNotExist:
            pass
        else:
            for field in ["original", "type", "source", "source_type", "source_id"]:
                self.fields[field].initial = getattr(image, field)
