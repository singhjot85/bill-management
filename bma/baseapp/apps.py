from django.apps import AppConfig


class BaseappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'bma.baseapp'
    verbose_name = "Customer"
    verbose_name_plural = "Customers"
