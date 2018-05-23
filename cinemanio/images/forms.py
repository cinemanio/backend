from django import forms
from django.utils.translation import ugettext_lazy as _

from cinemanio.images.widgets import AdminImagePreviewWidget, ForeignKeyRawIdWidget1
from cinemanio.images.models import Image


class ImageInlineForm(forms.ModelForm):
    image_url = forms.CharField(label=_('Preview'), required=False, widget=AdminImagePreviewWidget())
    type = forms.ChoiceField(label=_('Type'), required=True, choices=(('', _('Select')),) + Image.TYPE_CHOICES)
    source = forms.CharField(label=_('Source'), required=False, max_length=100)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['image'].required = False
        self.fields['image'].widget = ForeignKeyRawIdWidget1(self._meta.model._meta.get_field('image').related_model)
        try:
            image = self.instance.image
        except Image.DoesNotExist:
            pass
        else:
            self.fields['image_url'].initial = image.original
            self.fields['type'].initial = image.type
            self.fields['source'].initial = image.source

    # def clean_image(self):
    #     return self.cleaned_data.get('image') or Image()
    #
    # def clean(self):
    #     """
    #     Get image_url, download image, create link and substitute link_id to the form
    #     """
    #     image = self.cleaned_data.get('image')
    #     source = self.cleaned_data.get('source', '')
    #     image_url = self.cleaned_data.get('image_url')
    #     try:
    #         type = int(self.cleaned_data.get('type'))
    #     except:
    #         type = None
    #
    #     if image and image.id:
    #         if type and image.type != type or source and image.source != source:
    #             # переопределяем поля картинки, если они поменялись
    #             image.type = type
    #             image.source = source
    #             image.save()
    #         elif not type:
    #             # Определяем необходимые поля, для существующей картинки
    #             self.cleaned_data['type'] = image.type # почему-то все равно выдается ошибка валидации формы
    #     else:
    #         if image_url and type:
    #             # заливаем новую картинку
    #             try:
    #                 image = Image.objects.download(image_url, type=type)
    #             except ImageWrongType:
    #                 raise forms.ValidationError(_('You entered wrong url of jpeg file: %s') % image_url)
    #             except:
    #                 raise forms.ValidationError(_('You already downloaded jpeg file: %s') % image_url)
    #
    #             self.cleaned_data['image'] = image
    #         else:
    #             raise forms.ValidationError(_('You have to specified new image correctly'))
    #
    #     self.cleaned_data = super(ImageInlineForm, self).clean()
    #     return self.cleaned_data
