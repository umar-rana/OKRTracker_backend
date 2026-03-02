from django.apps import AppConfig


class OkrAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'okr_app'

    def ready(self):
        import okr_app.signals
