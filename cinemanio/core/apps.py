from django.contrib.admin.apps import AdminConfig as AdminConfigBase
from django.apps import AppConfig as AppConfigBase


class AppConfig(AppConfigBase):
    name = 'cinemanio.core'


class AdminConfig(AdminConfigBase):
    default_site = 'cinemanio.core.admin.site.AdminSite'
