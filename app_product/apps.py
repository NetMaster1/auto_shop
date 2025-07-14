from django.apps import AppConfig


class AppProductConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app_product'

    # def ready(self):
    #     from jobs import updater
    #     updater.start()

