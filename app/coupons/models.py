from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Coupon(models.Model):
    """
    Represents a discount coupon that can be applied to orders.

    This model stores information about a coupon, including its unique code,
    validity period, discount percentage, and active status.

    Attributes:
        code (models.CharField): The unique code for the coupon (e.g., "SAVE10").
            It has a maximum length of 50 characters.
        valid_from (models.DateTimeField): The date and time from which the coupon
            is valid.
        valid_to (models.DateTimeField): The date and time until which the coupon
            is valid.
        discount (models.IntegerField): The discount percentage offered by the coupon.
            Must be between 0 and 100.
        active (models.BooleanField): A boolean indicating whether the coupon is
            currently active and can be used.
    """
    code = models.CharField(max_length=50, unique=True)
    valid_from = models.DateTimeField()
    valid_to = models.DateTimeField()
    discount = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Percentage vaule (0 to 100)",
    )
    active = models.BooleanField()

    def __str__(self):
        """
        Returns the string representation of the object.

        This method is essential for displaying a meaningful name for instances
        in the Django admin and when the object is printed.

        Returns:
            str: The code associated with the object.
        """
        return self.code
