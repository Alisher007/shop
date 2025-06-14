from django.apps import AppConfig


class CouponsConfig(AppConfig):
    """
    Configuration for the 'coupons' Django application.

    This class sets the default auto field type for models within the
    'coupons' app and registers its name with Django's application system.
    """
    default_auto_field = "django.db.models.BigAutoField"
    name = "coupons"
