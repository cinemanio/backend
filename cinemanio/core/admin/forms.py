from django import forms

from cinemanio.core.admin.widgets import FastForeignKeyRawIdWidget


class CastInlineForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in ['person', 'movie', 'role']:
            self.fields[field].widget = FastForeignKeyRawIdWidget(self._meta.model._meta.get_field(field).remote_field,
                                                                  instance=self.instance, field=field)
