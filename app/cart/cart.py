from decimal import Decimal

from django.conf import settings

from coupons.models import Coupon
from shop.models import Product


class Cart:
    """
    A representation of the shopping cart stored in the user's session.

    This class provides methods for adding, removing, updating, and iterating
    over products in the cart. It also handles the application of coupons
    and calculation of total prices.
    """
    def __init__(self, request):
        """
        Initializes the cart.

        Retrieves the cart data from the user's session. If no cart exists
        in the session, an empty cart is created and saved. It also attempts
        to load any coupon ID stored in the session.

        Args:
            request (HttpRequest): The current HTTP request object, used to
                                   access the user's session.
        """
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            # save an empty cart in the session
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart
        # store current applied coupon
        self.coupon_id = self.session.get("coupon_id")

    def __iter__(self):
        """
        Iterates over the items in the cart and fetches product details from the database.

        For each item in the cart, it retrieves the corresponding `Product` object,
        converts the stored price to a Decimal, and calculates the total price
        for that item (`price * quantity`).

        Yields:
            dict: A dictionary for each item in the cart, including the `Product`
                  object, its price (as Decimal), quantity, and calculated total price.
        """
        product_ids = self.cart.keys()
        # get the product objects and add them to the cart
        products = Product.objects.filter(id__in=product_ids)
        cart = self.cart.copy()
        for product in products:
            cart[str(product.id)]["product"] = product
        for item in cart.values():
            item["price"] = Decimal(item["price"])
            item["total_price"] = item["price"] * item["quantity"]
            yield item

    def __len__(self):
        """
        Counts the total number of items (quantities) in the cart.

        Returns:
            int: The sum of the quantities of all products in the cart.
        """
        return sum(item["quantity"] for item in self.cart.values())

    def add(self, product, quantity=1, override_quantity=False):
        """
        Adds a product to the cart or updates its quantity.

        If the product is already in the cart:
        - If `override_quantity` is True, the existing quantity is replaced.
        - If `override_quantity` is False, the new quantity is added to the existing one.
        If the product is not in the cart, it's added with the specified quantity and price.

        Args:
            product (Product): The `Product` model instance to add or update.
            quantity (int, optional): The quantity to add or set. Defaults to 1.
            override_quantity (bool, optional): If True, replaces existing quantity.
                                                If False, adds to existing quantity.
                                                Defaults to False.
        """
        product_id = str(product.id)
        if product_id not in self.cart:
            self.cart[product_id] = {"quantity": 0, "price": str(product.price)}
        if override_quantity:
            self.cart[product_id]["quantity"] = quantity
        else:
            self.cart[product_id]["quantity"] += quantity
        self.save()

    def save(self):
        """
        Marks the session as modified to ensure the cart data is saved.

        This method should be called after any changes are made to `self.cart`.
        """
        self.session.modified = True

    def remove(self, product):
        """
        Removes a specific product from the cart.

        If the product is found in the cart, it is deleted and the session is saved.

        Args:
            product (Product): The `Product` model instance to remove.
        """
        product_id = str(product.id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    def clear(self):
        """
        Removes the entire cart from the session.

        This effectively empties the shopping cart.
        """
        del self.session[settings.CART_SESSION_ID]
        self.save()

    def get_total_price(self):
        """
        Calculates the total price of all items currently in the cart, before discounts.

        Returns:
            Decimal: The sum of (item price * item quantity) for all items in the cart.
        """
        return sum(
            Decimal(item["price"]) * item["quantity"] for item in self.cart.values()
        )

    @property
    def coupon(self):
        """
        Retrieves the `Coupon` object currently applied to the cart.

        It attempts to fetch the coupon from the database using the `coupon_id`
        stored in the session.

        Returns:
            Coupon or None: The `Coupon` object if a valid coupon ID is found
                            and the coupon exists, otherwise None.
        """
        if self.coupon_id:
            try:
                return Coupon.objects.get(id=self.coupon_id)
            except Coupon.DoesNotExist:
                pass
        return None

    def get_discount(self):
        """
        Calculates the monetary discount amount based on the applied coupon.

        Returns:
            Decimal: The calculated discount amount. Returns 0 if no coupon
                     is applied or if the coupon has no discount.
        """
        if self.coupon:
            return (self.coupon.discount / Decimal(100)) * self.get_total_price()
        return Decimal(0)

    def get_total_price_after_discount(self):
        """
        Calculates the total price of the cart after applying any coupon discount.

        Returns:
            Decimal: The final total price of the cart.
        """
        return self.get_total_price() - self.get_discount()
