from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import include, path

admin.autodiscover()
admin.site.enable_nav_sidebar = False

urlpatterns = [
    path("accounts/", include("allauth.urls")),
    path("admin/", admin.site.urls),
    path("cart/", include("cart.urls", namespace="cart")),
    path("orders/", include("orders.urls", namespace="orders")),
    path("coupons/", include("coupons.urls", namespace="coupons")),
    path("payment/", include("payments.urls", namespace="payment")),
    path("", include("shop.urls", namespace="shop")),
]

if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


admin.site.site_header = "shop admin"
admin.site.site_title = "shop admin"
admin.site.site_url = "https://shop.com/"
admin.site.index_title = "shop administration"
