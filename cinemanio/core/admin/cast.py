from django.contrib import admin
# from django.forms.models import BaseInlineFormSet

from cinemanio.core.models import Cast


# class MyInlineFormset(BaseInlineFormSet):
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.queryset = self.queryset.select_related('role', 'person', 'movie')
#         print(self.queryset.query)
#         # self.queryset = Cast.objects.select_related('role').prefetch_related('person', 'movie')
#
#     def get_queryset(self):
#         return super().get_queryset().select_related('role', 'person', 'movie')


class CastInline(admin.TabularInline):
    """
    Cast on Movie or career on Person pages in admin
    """
    model = Cast
    classes = ('collapse', 'collapsed',)
    # raw_id_fields = ['movie', 'person', 'role']
    # fields = ['movie', 'person', 'role']
    autocomplete_fields = ['movie', 'person']
    extra = 0
    # formset = MyInlineFormset

    # def get_queryset(self, request):
    #     # TODO: it doesn't work, fix it
    #     # print(super().get_queryset(request).select_related('role').query)
    #     return super().get_queryset(request).select_related('role')#.prefetch_related('person', 'movie')
