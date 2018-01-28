from django.apps import AppConfig


class AppConfig(AppConfig):
    name = 'cinemanio.attitures'

    def ready(self):
        import cinemanio.attitudes.signals
