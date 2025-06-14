import stripe
from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from orders.models import Order

from .tasks import payment_completed


@csrf_exempt
def stripe_webhook(request):
    """
    Handles Stripe webhook events for payment processing.

    This view listens for incoming POST requests from Stripe's webhook service.
    It verifies the webhook signature to ensure the request's authenticity
    and processes specific event types, such as `checkout.session.completed`.

    Upon a successful `checkout.session.completed` event for a payment, it
    updates the corresponding order in the database by marking it as paid
    and storing the Stripe payment ID. It then triggers an asynchronous task
    for post-payment processing (e.g., sending email notifications).

    Args:
        request (HttpRequest): The HTTP request object, containing the Stripe
                               webhook payload in its body and signature in headers.

    Returns:
        HttpResponse:
            - HTTP 200 OK if the event is processed successfully.
            - HTTP 400 Bad Request if the payload is invalid or the signature
              verification fails.
            - HTTP 404 Not Found if the associated order cannot be found.
    """
    payload = request.body
    sig_header = request.META["HTTP_STRIPE_SIGNATURE"]
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET,
        )
    except ValueError:
        # Invalid payload
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError:
        # Invalid signature
        return HttpResponse(status=400)

    if event.type == "checkout.session.completed":
        session = event.data.object
        if session.mode == "payment" and session.payment_status == "paid":
            try:
                order = Order.objects.get(id=session.client_reference_id)
            except Order.DoesNotExist:
                return HttpResponse(status=404)
            # mark order as paid
            order.paid = True
            # store Stripe payment ID
            order.stripe_id = session.payment_intent
            order.save()
            # launch asynchronous task
            payment_completed.delay(order.id)

    return HttpResponse(status=200)
