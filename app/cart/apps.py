from django.apps import AppConfig


class CartConfig(AppConfig):
    """
    Configuration for the 'cart' Django application.

    This class sets the default auto field type for models within the
    'cart' app and registers its name with Django's application system.
    """
    default_auto_field = "django.db.models.BigAutoField"
    name = "cart"
