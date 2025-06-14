import csv
import datetime

from django.contrib import admin
from django.http import HttpResponse
from django.urls import reverse
from django.utils.safestring import mark_safe

from .models import Order, OrderItem


def export_to_csv(modeladmin, queryset):
    """
    Exports the selected queryset data to a CSV file.

    This Django admin action generates a CSV file containing data from the
    objects in the provided queryset. It automatically creates a header row
    with verbose field names and formats datetime fields.

    Args:
        modeladmin (ModelAdmin): The current ModelAdmin instance.
        request (HttpRequest): The current HTTP request object.
        queryset (QuerySet): The queryset of objects selected in the admin
            for export.

    Returns:
        HttpResponse: A CSV file as an HTTP response, with the
            'Content-Disposition' header set to trigger a download.
    """
    opts = modeladmin.model._meta
    content_disposition = f"attachment; filename={opts.verbose_name}.csv"
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = content_disposition
    writer = csv.writer(response)
    fields = [
        field
        for field in opts.get_fields()
        if not field.many_to_many and not field.one_to_many
    ]
    # Write a first row with header information
    writer.writerow([field.verbose_name for field in fields])
    # Write data rows
    for obj in queryset:
        data_row = []
        for field in fields:
            value = getattr(obj, field.name)
            if isinstance(value, datetime.datetime):
                value = value.strftime("%d/%m/%Y")
            data_row.append(value)
        writer.writerow(data_row)
    return response


export_to_csv.short_description = "Export to CSV"


class OrderItemInline(admin.TabularInline):
    """
    Django Admin TabularInline for `OrderItem` model.

    This inline allows `OrderItem` objects to be edited directly on the
    `Order` change page in the Django administration site. It displays
    order items in a compact, table-like format.

    Attributes:
        model (Model): The model to be displayed inline (OrderItem).
        raw_id_fields (list): Fields that will be displayed as a raw ID
                              input field, useful for ForeignKey fields with
                              many options (e.g., 'product').
    """
    model = OrderItem
    raw_id_fields = ["product"]


def order_payment(obj):
    """
    Generates an HTML link to the Stripe payment page or transaction.

    This function is intended for use in the Django admin interface or similar
    contexts where an `Order` object (or an object with a `get_stripe_url`
    method and `stripe_id` attribute) is passed. It creates a clickable link
    to the corresponding Stripe transaction if a `stripe_id` exists.

    Args:
        obj: An object (presumably an Order instance) that has:
            - a `get_stripe_url()` method returning a URL.
            - a `stripe_id` attribute.

    Returns:
        str: An HTML string containing a link to the Stripe transaction if
             `obj.stripe_id` is present, otherwise an empty string.
    """
    url = obj.get_stripe_url()
    if obj.stripe_id:
        html = f'<a href="{url}" target="_blank">{obj.stripe_id}</a>'
        return mark_safe(html)
    return ""


order_payment.short_description = "Stripe payment"


def order_detail(obj):
    """
    Generates an HTML link to the detailed admin page for a given order.

    This function is designed to be used in the Django admin interface or similar
    contexts. It creates a clickable "View" link that navigates to the
    administrative detail page for the provided order object.

    Args:
        obj: An order object (e.g., an instance of an Order model)
             that has an `id` attribute.

    Returns:
        str: An HTML string containing a link to the order's admin detail page.
    """
    url = reverse("orders:admin_order_detail", args=[obj.id])
    return mark_safe(f'<a href="{url}">View</a>')


def order_pdf(obj):
    """
    Generates an HTML link to the detailed admin page for a given order.

    This function is designed to be used in the Django admin interface or similar
    contexts. It creates a clickable "View" link that navigates to the
    administrative detail page for the provided order object.

    Args:
        obj: An order object (e.g., an instance of an Order model)
             that has an `id` attribute.

    Returns:
        str: An HTML string containing a link to the order's admin detail page.
    """
    url = reverse("orders:admin_order_pdf", args=[obj.id])
    return mark_safe(f'<a href="{url}">PDF</a>')


order_pdf.short_description = "Invoice"


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """
    Django Admin configuration for the `Order` model.

    This class customizes how `Order` objects are displayed and managed
    within the Django administration site. It provides detailed list display,
    filtering options, inline editing for associated order items, and custom
    actions for viewing order details, payment links, PDF invoices, and CSV export.

    Attributes:
        list_display (list): Fields and custom methods to display in the
                              change list view for orders.
        list_filter (list): Fields to use for filtering options in the sidebar
                             of the change list view.
        inlines (list): A list of `TabularInline` or `StackedInline` subclasses
                        to allow editing of related objects on the same page as the parent.
        actions (list): Custom admin actions available for selected orders.
    """
    list_display = [
        "id",
        "first_name",
        "last_name",
        "email",
        "address",
        "postal_code",
        "city",
        "paid",
        order_payment,
        "created",
        "updated",
        order_detail,
        order_pdf,
    ]
    list_filter = ["paid", "created", "updated"]
    inlines = [OrderItemInline]
    actions = [export_to_csv]
