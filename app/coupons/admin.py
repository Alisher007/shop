from django.contrib import admin

from .models import Coupon


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    """
    Django Admin configuration for the `Coupon` model.

    This class customizes how `Coupon` objects are displayed and managed
    within the Django administration site. It provides clear list display,
    filtering capabilities, and search functionality for coupon codes.

    Attributes:
        list_display (list): Fields to display in the change list view for coupons.
        list_filter (list): Fields to use for filtering options in the sidebar.
        search_fields (list): Fields that can be searched from the admin search bar.
    """
    list_display = ["code", "valid_from", "valid_to", "discount", "active"]
    list_filter = ["active", "valid_from", "valid_to"]
    search_fields = ["code"]
