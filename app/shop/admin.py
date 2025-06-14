from django.contrib import admin

from .models import Category, Product


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """
    Django Admin configuration for the `Category` model.

    This class customizes how `Category` objects are displayed and managed
    within the Django administration site.

    Attributes:
        list_display (list): Fields to display in the change list view.
        prepopulated_fields (dict): Fields that are automatically populated
                                    using other fields (e.g., `slug` from `name`).
    """
    list_display = ["name", "slug"]
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """
    Django Admin configuration for the `Product` model.

    This class customizes how `Product` objects are displayed and managed
    within the Django administration site, offering filtering, inline editing,
    and slug prepopulation.

    Attributes:
        list_display (list): Fields to display in the change list view.
        list_filter (list): Fields to use for filtering options in the sidebar.
        list_editable (list): Fields that can be edited directly from the change list view.
        prepopulated_fields (dict): Fields that are automatically populated
                                    using other fields (e.g., `slug` from `name`).
    """
    list_display = ["name", "slug", "price", "available", "created", "updated"]
    list_filter = ["available", "created", "updated"]
    list_editable = ["price", "available"]
    prepopulated_fields = {"slug": ("name",)}
