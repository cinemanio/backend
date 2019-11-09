from django.urls.base import reverse
from django.conf.urls import url
from django.contrib import admin
from django.template.response import TemplateResponse

from cinemanio.core.models import Movie, Person, Cast
from cinemanio.core.utils.languages import iter_languages


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
        ] + [
            f'No Wikipedia {lang.upper()}' for lang in iter_languages()
        ] + [
            'iMDB outdated',
            'Kinopoisk outdated',
        ] + [
            f'Wikipedia {lang.upper()} outdated' for lang in iter_languages()
        ]

    def get_model_stat(self, model):
        total = model.objects.count()
        context = {'total': total}
        if model != Cast:
            imdb = model.sites.with_site('imdb').count()
            kinopoisk = model.sites.with_site('kinopoisk').count()
            context.update(self.get_site_stat(model, total, imdb, 'imdb'))
            context.update(self.get_site_stat(model, total, kinopoisk, 'kinopoisk'))
            for lang in iter_languages():
                wikipedia = model.sites.with_site('wikipedia', lang).count()
                context.update(self.get_site_stat(model, total, wikipedia, 'wikipedia', lang))
        return context

    def get_site_stat(self, model, total, count, name, lang=None):
        prefix = f'{name}_{lang}' if lang else name
        return {
            f'{prefix}__present': count,
            f'{prefix}__no': total - count,
            f'{prefix}__outdated': model.sites.with_site_outdated(name, lang).count(),
        }


site = AdminSite(name='admin')
admin.site = site
