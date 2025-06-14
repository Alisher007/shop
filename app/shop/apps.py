from django.apps import AppConfig


class ShopConfig(AppConfig):
    """
    Configuration for the 'shop' Django application.

    This class sets up the default auto field type for models within the
    'shop' app and specifies its name for Django's application registry.
    """
    default_auto_field = "django.db.models.BigAutoField"
    name = "shop"
