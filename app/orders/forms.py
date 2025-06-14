from django import forms

from .models import Order


class OrderCreateForm(forms.ModelForm):
    """
    A Django ModelForm for creating new orders.

    This form is based on the `Order` model and includes fields for capturing
    essential customer and shipping information required to place an order.

    Fields:
        first_name (CharField): The customer's first name.
        last_name (CharField): The customer's last name.
        email (EmailField): The customer's email address.
        address (CharField): The customer's street address.
        postal_code (CharField): The customer's postal code.
        city (CharField): The customer's city.
    """
    class Meta:
        """
        Meta options for the `OrderCreateForm`.

        This inner class defines the associated model and the specific fields
        from that model that will be included in this form.
        """
        model = Order
        fields = ["first_name", "last_name", "email", "address", "postal_code", "city"]
