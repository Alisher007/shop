from decimal import Decimal

import stripe
from django.conf import settings
from django.shortcuts import get_object_or_404, redirect, render, reverse

from orders.models import Order

# create the Stripe instance
stripe.api_key = settings.STRIPE_SECRET_KEY
stripe.api_version = settings.STRIPE_API_VERSION


def payment_process(request):
    """
    Initiates the payment process for an order using Stripe Checkout.

    This view handles both GET and POST requests.
    For a GET request, it renders a payment processing page.
    For a POST request, it creates a Stripe Checkout Session based on the
    current order details, including line items and any applied coupons.
    It then redirects the user to the Stripe hosted payment page.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse:
            - For GET requests: Renders the 'payments/process.html' template.
            - For POST requests: Redirects to the Stripe Checkout Session URL
              to complete the payment.
    """
    order_id = request.session.get("order_id", None)
    order = get_object_or_404(Order, id=order_id)

    if request.method == "POST":
        success_url = request.build_absolute_uri(reverse("payment:completed"))
        cancel_url = request.build_absolute_uri(reverse("payment:canceled"))

        # Stripe checkout session data
        session_data = {
            "mode": "payment",
            "client_reference_id": order.id,
            "success_url": success_url,
            "cancel_url": cancel_url,
            "line_items": [],
        }
        # add order items to the Stripe checkout session
        for item in order.items.all():
            session_data["line_items"].append(
                {
                    "price_data": {
                        "unit_amount": int(item.price * Decimal("100")),
                        "currency": "usd",
                        "product_data": {
                            "name": item.product.name,
                        },
                    },
                    "quantity": item.quantity,
                },
            )

        # Stripe coupon
        if order.coupon:
            stripe_coupon = stripe.Coupon.create(
                name=order.coupon.code, percent_off=order.discount, duration="once",
            )
            session_data["discounts"] = [{"coupon": stripe_coupon.id}]

        # create Stripe checkout session
        session = stripe.checkout.Session.create(**session_data)

        # redirect to Stripe payment form
        return redirect(session.url, code=303)

    else:
        return render(request, "payments/process.html", locals())


def payment_completed(request):
    """
    Renders the payment completed page.

    This view is typically accessed after a successful payment transaction
    and simply displays a confirmation page to the user.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: Renders the 'payments/completed.html' template.
    """
    return render(request, "payments/completed.html")


def payment_canceled(request):
    """
    Renders the payment canceled page.

    This view is typically accessed after a successful payment transaction
    and simply displays a confirmation page to the user.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: Renders the 'payments/canceled.html' template.
    """
    return render(request, "payments/canceled.html")
