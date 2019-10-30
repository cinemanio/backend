from django.urls.base import reverse
from django.conf.urls import url
from django.contrib import admin
from django.template.response import TemplateResponse

from cinemanio.core.models import Movie, Person, Cast


class AdminSite(admin.AdminSite):
    def get_urls(self):
        urls = super(AdminSite, self).get_urls()
        admin_view = self.admin_view

        custom_urls = [
            url(r'statistic/$', admin_view(self.my_view), name="statistic"),
        ]
        return custom_urls + urls

    def my_view(self, request):
        context = dict(
            self.each_context(request),
            titles=self.get_titles(),
            movie=self.prep_context(Movie),
            person=self.prep_context(Person),
            cast=self.get_model_stat(Cast),
        )
        return TemplateResponse(request, "admin/statistic.html", context)

    def prep_context(self, model):
        data = []
        stat = self.get_model_stat(model)

        for key, value in stat.items():
            url = reverse(f'admin:core_{model.__name__.lower()}_changelist')
            base_value = None
            if key != 'total':
                url += '?' + key.replace('__', '=')
                if 'present' in key:
                    continue
                elif 'outdated' in key:
                    base_value = stat[key.replace('outdated', 'present')]
                else:
                    base_value = stat['total']
            data.append((url, value, base_value))

        return data

    def get_titles(self):
        return [
            'Type',
            'Total count',
            'No iMDB',
            'No Kinopoisk',
            'No Wikipedia EN',
            'No Wikipedia RU',
            'iMDB outdated',
            'Kinopoisk outdated',
            'Wikipedia EN outdated',
            'Wikipedia RU outdated',
        ]

    def get_model_stat(self, model):
        total = model.objects.count()
        if model == Cast:
            return {'total': total}
        imdb = model.sites.with_site('imdb').count()
        kinopoisk = model.sites.with_site('kinopoisk').count()
        wikipedia_en = model.sites.with_site('wikipedia', 'en').count()
        wikipedia_ru = model.sites.with_site('wikipedia', 'ru').count()
        return {
            'total': total,
            'imdb__present': imdb,
            'kinopoisk__present': kinopoisk,
            'wikipedia_en__present': wikipedia_en,
            'wikipedia_ru__present': wikipedia_ru,
            'imdb__no': total - imdb,
            'kinopoisk__no': total - kinopoisk,
            'wikipedia_en__no': total - wikipedia_en,
            'wikipedia_ru__no': total - wikipedia_ru,
            'imdb__outdated': model.sites.with_site_outdated('imdb').count(),
            'kinopoisk__outdated': model.sites.with_site_outdated('kinopoisk').count(),
            'wikipedia_en__outdated': model.sites.with_site_outdated('wikipedia', 'en').count(),
            'wikipedia_ru__outdated': model.sites.with_site_outdated('wikipedia', 'ru').count(),
        }


site = AdminSite(name='admin')
admin.site = site
