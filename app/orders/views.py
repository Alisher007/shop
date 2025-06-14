import weasyprint
from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.urls import reverse

from cart.cart import Cart

from .forms import OrderCreateForm
from .models import Order, OrderItem
from .tasks import order_created


def order_create(request):
    """
    Handles the creation of a new order from the shopping cart.

    This view processes both GET and POST requests. For GET requests, it
    displays an empty order creation form. For POST requests, it attempts to
    validate the submitted order details.

    If the form is valid, it saves the order, populates it with items from the
    current cart (applying any active coupon), clears the cart, and then
    initiates an asynchronous task to handle further order processing (e.g., sending
    email confirmations). Finally, it redirects the user to the payment processing page.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse:
            - For GET requests: Renders the 'orders/orders_create.html' template
              with the cart contents and an empty order creation form.
            - For successful POST requests: Redirects to the payment processing view.
            - For invalid POST requests: Renders the 'orders/orders_create.html'
              template with the cart contents and the form containing validation errors.
    """
    cart = Cart(request)
    if request.method == "POST":
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            if cart.coupon:
                order.coupon = cart.coupon
                order.discount = cart.coupon.discount
            order.save()
            for item in cart:
                OrderItem.objects.create(
                    order=order,
                    product=item["product"],
                    price=item["price"],
                    quantity=item["quantity"],
                )
            # clear the cart
            cart.clear()
            # launch asynchronous task
            order_created.delay(order.id)
            # set the order in the session
            request.session["order_id"] = order.id
            # redirect for payment
            return redirect(reverse("payment:process"))
    else:
        form = OrderCreateForm()
    return render(request, "orders/orders_create.html", {"cart": cart, "form": form})


@staff_member_required
def admin_order_detail(request, order_id):
    """
    Displays the detailed view of a specific order in the Django admin.

    This view is restricted to staff members. It retrieves an order by its ID
    and renders a custom administrative detail template for it, providing
    a comprehensive overview of the order.

    Args:
        request (HttpRequest): The HTTP request object.
        order_id (int): The ID of the order to display.

    Returns:
        HttpResponse: Renders the 'admin/orders/detail.html' template with
            the retrieved order object in the context.
    """
    order = get_object_or_404(Order, id=order_id)
    return render(request, "admin/orders/detail.html", {"order": order})


@staff_member_required
def admin_order_pdf(request, order_id):
    """
    Generates a PDF invoice for a specific order.

    This view is accessible only to staff members. It fetches an order by its ID,
    renders an HTML template with the order details, and then converts that HTML
    into a PDF document using WeasyPrint. The generated PDF is returned as an
    HTTP response, prompting a download.

    Args:
        request (HttpRequest): The HTTP request object.
        order_id (int): The ID of the order for which to generate the PDF.

    Returns:
        HttpResponse: A PDF file as an HTTP response, with the
            'Content-Disposition' header set to trigger a download.
    """
    order = get_object_or_404(Order, id=order_id)
    html = render_to_string("orders/pdf.html", {"order": order})
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f"filename=order_{order.id}.pdf"
    weasyprint.HTML(string=html).write_pdf(
        response, stylesheets=[weasyprint.CSS(settings.STATIC_ROOT / "css/pdf.css")],
    )
    return response
