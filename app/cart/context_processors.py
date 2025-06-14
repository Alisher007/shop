from .cart import Cart


def cart(request):
    """
    Context processor that adds the current shopping cart to the template context.

    This makes the `cart` object available in all templates rendered by Django's
    `RequestContext` (or equivalent).

    Args:
        request (HttpRequest): The current HTTP request object.

    Returns:
        dict: A dictionary containing the `Cart` instance, accessible via the key "cart".
    """
    return {"cart": Cart(request)}
