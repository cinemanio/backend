from django.forms import ModelForm

from cinemanio.core.models import Movie
from cinemanio.core.utils.languages import translated_fields


class MovieForm(ModelForm):
    """
    Movie Form
    """
    class Meta:
        model = Movie
        fields = translated_fields('title', with_base=True) + (
            'year', 'runtime', 'novel_isbn',
            'sequel_for', 'prequel_for', 'remake_for', 'novel_isbn',
            'genres', 'languages', 'countries',
            'site_official_url', 'site_fan_url',
        )

    # def clean_sequel_for(self):
    #     return self.check_relation('sequel_for')
    #
    # def clean_prequel_for(self):
    #     return self.check_relation('prequel_for')
    #
    # def clean_remake_for(self):
    #     return self.check_relation('remake_for')
    #
    # def check_relation(self, field):
    #     u"""
    #     Обнуляем поля связей с другими фильмами, если в типе это не подтверждено
    #     Проверяем, что в поле не текущий фильм и что год фильма меньше года текущего фильма
    #     TODO: перенести проверки в модель как кастомные валидаторы
    #     (http://docs.djangoproject.com/en/dev/ref/validators/#ref-validators)
    #     и проверить тестами
    #     """
    #     types_fields_map = {
    #         'sequel_for': 11,
    #         'prequel_for': 15,
    #         'remake_for': 9,
    #         'novel_isbn': 8,
    #     }
    #
    #     movie = self.cleaned_data.get(field)
    #     if movie == self.instance:
    #         raise ValidationError(_("You can't link movie to itself"))
    #     if movie and movie.year > self.cleaned_data.get('year'):
    #         raise ValidationError(_("You can't specified movie, that was created later"))
    #
    #     id = types_fields_map.get(field)
    #     # при сохранении через админку self.cleaned_data.get('types') пуст, хотя через сайтовую форму заполнен,
    #     # поэтому используем словарь переданных данных self.data.get('types')
    #     if id not in [int(type) for type in dict(self.data).get('types', [])]:
    #         movie = None
    #
    #     return movie
