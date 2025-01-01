from django.apps import AppConfig


class SponsorAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'Sponsor_App'
    
    def ready(self):
        
        import Sponsor_App.signals