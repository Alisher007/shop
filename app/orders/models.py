from decimal import Decimal

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from coupons.models import Coupon
from shop.models import Product


class Order(models.Model):
    """
    Represents a customer order in the e-commerce system.

    This model stores all relevant information for a customer's order,
    including their shipping details, payment status, associated coupons,
    and the total cost.

    Attributes:
        first_name (str): The first name of the customer placing the order.
        last_name (str): The last name of the customer placing the order.
        email (str): The email address of the customer.
        address (str): The shipping address for the order.
        postal_code (str): The postal code for the shipping address.
        city (str): The city for the shipping address.
        created (datetime): The timestamp when the order was created.
            Automatically set on creation.
        updated (datetime): The timestamp when the order was last updated.
            Automatically updated on each save.
        paid (bool): A boolean indicating whether the order has been paid for.
            Defaults to `False`.
        stripe_id (str): The ID of the corresponding transaction in Stripe.
            Can be blank if no payment is associated yet.
        coupon (ForeignKey): A foreign key to the `Coupon` model, representing
            any discount coupon applied to this order. Can be `null` and `blank`.
        discount (int): The percentage discount applied to the order based on
            the coupon. Defaults to 0, and must be between 0 and 100.
    """
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField()
    address = models.CharField(max_length=250)
    postal_code = models.CharField(max_length=20)
    city = models.CharField(max_length=100)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    paid = models.BooleanField(default=False)
    stripe_id = models.CharField(max_length=250, blank=True)
    coupon = models.ForeignKey(
        Coupon, related_name="orders", null=True, blank=True, on_delete=models.SET_NULL,
    )
    discount = models.IntegerField(
        default=0, validators=[MinValueValidator(0), MaxValueValidator(100)],
    )

    class Meta:
        """
        Meta options for the Order model.

        This inner class provides metadata for the Order model, controlling
        its database ordering and indexing to optimize query performance.
        """
        ordering = ["-created"]
        indexes = [
            models.Index(fields=["-created"]),
        ]

    def __str__(self):
        """
        Returns a human-readable string representation of the Order object.

        This method is essential for displaying a meaningful name for order
        instances in the Django admin and when they're printed.

        Returns:
            str: The string "Order" followed by the order's ID.
        """
        return f"Order {self.id}"

    def get_total_cost_before_discount(self):
        """
        Calculates the total cost of all items in the order *before* any discounts are applied.

        It sums the cost of each individual order item.

        Returns:
            Decimal: The total cost of all items in the order prior to discount application.
        """
        return sum(item.get_cost() for item in self.items.all())

    def get_discount(self):
        """
        Calculates the monetary discount amount for the order based on the `discount` percentage.

        The discount is applied to the total cost before any discounts.

        Returns:
            Decimal: The calculated discount amount. Returns 0 if no discount is applied.
        """
        total_cost = self.get_total_cost_before_discount()
        if self.discount:
            return total_cost * (self.discount / Decimal(100))
        return Decimal(0)

    def get_total_cost(self):
        """
        Calculates the final total cost of the order *after* applying any discounts.

        This is the net amount the customer needs to pay.

        Returns:
            Decimal: The total cost of the order after the discount has been deducted.
        """
        total_cost = self.get_total_cost_before_discount()
        return total_cost - self.get_discount()

    def get_stripe_url(self):
        """
        Constructs and returns the URL to the corresponding transaction in the Stripe Dashboard.

        The URL varies based on whether the application is configured for
        Stripe's test mode or live mode.

        Returns:
            str: The URL to the Stripe payment transaction, or an empty string
                 if `stripe_id` is not associated with the order.
        """
        if not self.stripe_id:
            # no payment associated
            return ""
        if "_test_" in settings.STRIPE_SECRET_KEY:
            # Stripe path for test payments
            path = "/test/"
        else:
            # Stripe path for real payments
            path = "/"
        return f"https://dashboard.stripe.com{path}payments/{self.stripe_id}"


class OrderItem(models.Model):
    """
    Represents a single item within a customer's order.

    This model links a specific product to an order, storing its price at the
    time of purchase and the quantity ordered.

    Attributes:
        order (ForeignKey): A foreign key to the `Order` model, indicating
            which order this item belongs to. Deleting an order will delete
            its associated items.
        product (ForeignKey): A foreign key to the `Product` model, identifying
            the product being ordered. Deleting a product will delete its
            associated order items.
        price (DecimalField): The price of the product at the time it was added
            to the order. Stored as a decimal with a maximum of 10 digits and
            2 decimal places.
        quantity (PositiveIntegerField): The quantity of the product ordered.
            Defaults to 1 and must be a positive integer.
    """
    order = models.ForeignKey(Order, related_name="items", on_delete=models.CASCADE)
    product = models.ForeignKey(
        Product, related_name="order_items", on_delete=models.CASCADE,
    )
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        """
        Returns a string representation of the OrderItem object.

        This method is useful for quickly identifying an individual order item,
        especially in the Django admin interface or when debugging.

        Returns:
            str: The string representation of the order item's ID.
        """
        return str(self.id)

    def get_cost(self):
        """
        Calculates the total cost for this specific order item.

        The cost is determined by multiplying the item's price by its quantity.

        Returns:
            Decimal: The total cost of the order item.
        """
        return self.price * self.quantity
