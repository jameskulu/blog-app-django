from django.apps import AppConfig


class AppConfig(AppConfig):
    name = 'App'

    def ready(self):
        import App.signals
