from django.apps import AppConfig


class OrdersConfig(AppConfig):
    """
    Configuration for the 'orders' Django application.

    This class sets the default auto field type for models within the
    'orders' app and registers its name with Django's application system.
    """
    default_auto_field = "django.db.models.BigAutoField"
    name = "orders"
