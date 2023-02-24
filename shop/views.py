from django.shortcuts import render, get_object_or_404
from cart.forms import CartAddProductForm
from .models import Category, Product
from .recommender import Recommender

def product_list(request, category_slug=None):
    category = None
    categories = Category.objects.all()
    products = Product.objects.filter(available=True)
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)
    context = {
        'category': category,
        'categories': categories,
        'products': products
    }
    return render(request, 'shop/shop_list.html', context)

def product_detail(request, id, slug):
    product = get_object_or_404(Product,
                            id=id,
                            slug=slug,
                            available=True)
    
    cart_product_form = CartAddProductForm()
    r = Recommender()
    recommended_products = r.suggest_products_for([product], 2)
    print(' recommended_products r ############## ', r)
    print(' recommended_products ############## ', recommended_products)
    context = {
        'product': product,
        'cart_product_form': cart_product_form,
        'recommended_products': recommended_products,
    }
    return render(request,'shop/shop_detail.html',context)

