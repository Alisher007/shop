from django import forms


class CouponApplyForm(forms.Form):
    """
    A simple form for applying a coupon code.

    This form provides a single field for users to input a coupon code
    they wish to apply to their order.

    Attributes:
        code (forms.CharField): The field for entering the coupon code.
    """
    code = forms.CharField()
