from django.apps import AppConfig


class ConfiguracionConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "configuracion"
    verbose_name = "Configuracion"

    def ready(self) -> None:
        from . import openapi  # noqa: F401
