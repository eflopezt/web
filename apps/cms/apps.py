from django.apps import AppConfig


class CmsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.cms"
    verbose_name = "Contenido del sitio (CMS)"

    def ready(self):
        # Importa señales si las agregamos más adelante
        pass
