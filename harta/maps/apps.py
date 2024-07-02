from django.apps import AppConfig

class MapsConfig(map):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'maps'

    def ready(self):
        from harta.harta import scheduler
        scheduler.start()