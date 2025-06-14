from django.db import models
from django.urls import reverse


class Category(models.Model):
    """
    Represents a product category in the e-commerce store.

    Categories are used to organize products and enable filtering by type.
    Each category has a unique name and a slug for URL generation.

    Attributes:
        name (str): The name of the category (e.g., 'Electronics', 'Books').
            Maximum length is 200 characters.
        slug (str): A unique, URL-friendly identifier for the category.
            Maximum length is 200 characters and must be unique.
    """
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)

    class Meta:
        """
        Meta options for the Category model.

        This inner class provides metadata for the Category model, controlling
        its behavior in various parts of Django, such as the database
        ordering, indexing, and display names in the administrative interface.
        """
        ordering = ["name"]
        indexes = [
            models.Index(fields=["name"]),
        ]
        verbose_name = "category"
        verbose_name_plural = "categories"

    def __str__(self):
        """
        Returns the category name as its string representation.
        This is used in the Django admin and when the object is converted to a string.
        """
        return self.name

    def get_absolute_url(self):
        """
        Returns the absolute URL to the list of products for this category.

        This URL is used to link directly to a page that displays all products
        belonging to this specific category.

        Returns:
            str: The URL for the category's product list page.
        """
        return reverse("shop:product_list_by_category", args=[self.slug])


class Product(models.Model):
    """
    Represents a product available in the e-commerce store.

    This model stores all essential details for a product, including its
    category, pricing, availability, and descriptive information.

    Attributes:
        category (ForeignKey): A foreign key to the `Category` model, linking
            the product to its respective category. Deleting a category will
            cascade and delete its associated products.
        name (str): The name of the product. Maximum length is 200 characters.
        slug (str): A URL-friendly identifier for the product, used in URLs
            for product detail pages. Maximum length is 200 characters.
        image (ImageField): An optional image for the product. Images are uploaded
            to `products/YEAR/MONTH/DAY/` relative to the media root.
        description (str): An optional detailed description of the product.
        price (DecimalField): The price of the product. Stored as a decimal
            with a maximum of 10 digits and 2 decimal places.
        available (bool): A boolean indicating whether the product is
            currently available for purchase. Defaults to `True`.
        created (datetime): The timestamp when the product was added to the
            database. Automatically set on creation.
        updated (datetime): The timestamp when the product was last updated.
            Automatically updated on each save.
    """
    category = models.ForeignKey(
        Category, related_name="products", on_delete=models.CASCADE,
    )
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200)
    image = models.ImageField(upload_to="products/%Y/%m/%d", blank=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    available = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        """
        Meta options for the Product model.

        This inner class provides metadata for the Product model, controlling
        its default ordering in database queries and defining database indexes
        to enhance lookup performance.
        """
        ordering = ["name"]
        indexes = [
            models.Index(fields=["id", "slug"]),
            models.Index(fields=["name"]),
            models.Index(fields=["-created"]),
        ]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        """
        Returns the absolute URL to the product's detail page.

        This URL is constructed using the product's ID and slug, making it
        SEO-friendly and unique for each product.

        Returns:
            str: The full URL to the product detail page.
        """
        return reverse("shop:product_detail", args=[self.id, self.slug])
