from django.apps import AppConfig


class LembaAppConfig(AppConfig):
    name = "lemba_app"


def ready(self):
    import lemba_app.signals
