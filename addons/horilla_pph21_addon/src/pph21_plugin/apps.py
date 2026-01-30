from django.apps import AppConfig


class Pph21PluginConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "pph21_plugin"

    def ready(self):
        from pph21_plugin import signals  # noqa: F401
        from pph21_plugin.urlpatch import patch_employee_urls

        patch_employee_urls()
