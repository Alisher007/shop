from django import forms

PRODUCT_QUANTITY_CHOICES = [(i, str(i)) for i in range(1, 21)]


class CartAddProductForm(forms.Form):
    """
    A form for adding products to the shopping cart.

    This form handles the quantity of a product to be added and whether to
    override the existing quantity in the cart.

    Attributes:
        quantity (forms.TypedChoiceField): The quantity of the product to add,
            chosen from `PRODUCT_QUANTITY_CHOICES` and coerced to an integer.
        override (forms.BooleanField): A hidden field indicating whether to
            override the current quantity of the product in the cart.
            Defaults to `False`.
    """
    quantity = forms.TypedChoiceField(choices=PRODUCT_QUANTITY_CHOICES, coerce=int)
    override = forms.BooleanField(
        required=False, initial=False, widget=forms.HiddenInput,
    )
