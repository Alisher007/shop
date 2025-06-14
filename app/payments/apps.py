from django.apps import AppConfig


class PaymentsConfig(AppConfig):
    """
    Configuration for the 'payments' Django application.

    This class sets the default auto field type for models within the
    'payments' app and registers its name with Django's application system.
    """
    default_auto_field = "django.db.models.BigAutoField"
    name = "payments"
