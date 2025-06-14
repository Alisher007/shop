from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from redis.exceptions import RedisError

from coupons.forms import CouponApplyForm
from shop.models import Product
from shop.recommender import Recommender

from .cart import Cart
from .forms import CartAddProductForm


@require_POST
def cart_add(request, product_id):
    """
    Adds a product to the shopping cart.

    This view handles adding a specified quantity of a product to the user's
    cart. It expects a POST request containing the product quantity and an
    optional override flag.

    Args:
        request (HttpRequest): The HTTP request object. Expected to be a POST request.
        product_id (int): The ID of the product to be added to the cart.

    Returns:
        HttpResponseRedirect: Redirects to the cart detail page after
            successfully adding the product. If the form is invalid,
            it still redirects to the cart detail page.
    """
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    form = CartAddProductForm(request.POST)
    if form.is_valid():
        cd = form.cleaned_data
        cart.add(
            product=product, quantity=cd["quantity"], override_quantity=cd["override"],
        )
    return redirect("cart:cart_detail")


@require_POST
def cart_remove(request, product_id):
    """
    Removes a product from the shopping cart.

    This view handles the removal of a specific product from the user's
    shopping cart. It expects a POST request.

    Args:
        request (HttpRequest): The HTTP request object. Expected to be a POST request.
        product_id (int): The ID of the product to be removed from the cart.

    Returns:
        HttpResponseRedirect: Redirects to the cart detail page after
            successfully removing the product.
    """
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)
    return redirect("cart:cart_detail")


def cart_detail(request):
    """
    Displays the contents of the shopping cart.

    This view retrieves the current cart, prepares forms for updating product
    quantities, and includes a form for applying coupons. It also attempts
    to fetch product recommendations based on the items currently in the cart.
    In case of a Redis error during recommendation generation, it gracefully
    handles the error and proceeds without recommendations.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: Renders the 'cart/cart_detail.html' template with the
            cart details, coupon application form, and recommended products
            (if available).
    """
    cart = Cart(request)
    for item in cart:
        item["update_quantity_form"] = CartAddProductForm(
            initial={"quantity": item["quantity"], "override": True},
        )
    coupon_apply_form = CouponApplyForm()

    r = Recommender()
    cart_products = [item["product"] for item in cart]

    try:
        r = Recommender()
        cart_products = [item["product"] for item in cart]
    except RedisError as e:
        print("Redis error in product_detail:", e)
        cart_products = []  # Fallback to empty list

    if cart_products:
        recommended_products = r.suggest_products_for(cart_products, max_results=4)
    else:
        recommended_products = []

    context = {
        "cart": cart,
        "coupon_apply_form": coupon_apply_form,
        "recommended_products": recommended_products,
    }
    return render(request, "cart/cart_detail.html", context)
