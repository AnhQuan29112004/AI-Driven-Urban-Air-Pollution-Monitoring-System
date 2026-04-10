from django.apps import AppConfig


class UserConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'air_pollution_be'

    def ready(self):
        import air_pollution_be.signals