from django.shortcuts import get_object_or_404, render
from redis.exceptions import RedisError

from cart.forms import CartAddProductForm

from .models import Category, Product
from .recommender import Recommender


def product_list(request, category_slug=None):
    """
    Displays a list of available products, optionally filtered by category.

    This view fetches all active categories and available products. If a
    `category_slug` is provided in the URL, it filters the products to
    show only those belonging to the specified category.

    Args:
        request (HttpRequest): The HTTP request object.
        category_slug (str, optional): The slug of the category to filter products by.
                                       Defaults to None, displaying all products.

    Returns:
        HttpResponse: Renders the 'shop/shop_list.html' template with:
            - `category`: The currently selected category object (or None if no filter).
            - `categories`: A queryset of all available categories.
            - `products`: A queryset of available products, potentially filtered by category.
    """
    category = None
    categories = Category.objects.all()
    products = Product.objects.filter(available=True)
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)
    context = {"category": category, "categories": categories, "products": products}
    return render(request, "shop/shop_list.html", context)


def product_detail(request, product_id, slug):
    """
    Displays the detailed information for a single product.

    This view retrieves a specific product by its ID and slug. It also
    prepares a form for adding the product to the cart and attempts to
    generate product recommendations based on the current product. It includes
    error handling for Redis connection issues during recommendation generation.

    Args:
        request (HttpRequest): The HTTP request object.
        product_id (int): The ID of the product to display.
        slug (str): The slug of the product, used to create SEO-friendly URLs.

    Returns:
        HttpResponse: Renders the 'shop/shop_detail.html' template with:
            - `product`: The detailed product object.
            - `cart_product_form`: A form for adding the product to the cart.
            - `recommended_products`: A list of recommended product objects. This
                                      will be an empty list if Redis is unavailable
                                      or no recommendations are found.
    """
    product = get_object_or_404(Product, id=product_id, slug=slug, available=True)

    cart_product_form = CartAddProductForm()

    try:
        r = Recommender()
        recommended_products = r.suggest_products_for([product], 2)
    except RedisError as e:
        print("Redis error in product_detail:", e)
        recommended_products = []  # Fallback to empty list

    context = {
        "product": product,
        "cart_product_form": cart_product_form,
        "recommended_products": recommended_products,
    }
    return render(request, "shop/shop_detail.html", context)
