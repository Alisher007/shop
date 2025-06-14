import redis
from django.conf import settings
from redis.exceptions import RedisError

from .models import Product


class Recommender:
    """
    A product recommender system that leverages Redis to store and retrieve
    "products purchased with" relationships.

    This class provides functionality to record product co-purchases and
    suggest related products based on that data. It gracefully handles
    Redis connection issues.
    """
    def __init__(self):
        """
        Initializes the Recommender by attempting to connect to a Redis instance.

        It uses connection details from Django's settings. If the connection fails,
        it prints an error and sets `self.redis` to None, allowing other methods
        to operate gracefully without Redis.
        """
        try:
            self.redis = redis.Redis(
                host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=settings.REDIS_DB,
            )
            # Test the connection to fail fast if Redis is down
            self.redis.ping()
        except RedisError as e:
            print("Redis connection failed:", e)
            self.redis = None

    def get_product_key(self, product_id):
        """
        Generates the Redis key used to store co-purchase data for a specific product.

        Args:
            product_id (int): The ID of the product.

        Returns:
            str: The Redis key string (e.g., "product:123:purchased_with").
        """
        return f"product:{product_id}:purchased_with"

    def products_bought(self, products):
        """
        Records that a list of products were purchased together.

        For each pair of different products in the provided list, it increments
        a counter in Redis, indicating that one product was purchased along with another.
        This data is used for generating recommendations. This operation is skipped
        if the Redis connection is not established.

        Args:
            products (list[Product]): A list of `Product` model instances that
                were purchased in the same order.
        """
        if not self.redis:
            return
        product_ids = [p.id for p in products]
        for product_id in product_ids:
            for with_id in product_ids:
                if product_id != with_id:
                    self.redis.zincrby(self.get_product_key(product_id), 1, with_id)

    def suggest_products_for(self, products, max_results=6):
        """
        Suggests related products based on co-purchase data for a given list of products.

        If a single product is provided, it returns products most frequently
        purchased with that product. If multiple products are provided, it
        combines the co-purchase data from all of them, removes the input
        products themselves, and returns the top suggestions. This operation
        is skipped if the Redis connection is not established.

        Args:
            products (list[Product]): A list of `Product` model instances
                for which to generate recommendations.
            max_results (int): The maximum number of recommended products to return.
                Defaults to 6.

        Returns:
            list[Product]: A list of `Product` model instances recommended based
                on co-purchase history, ordered by relevance. Returns an empty list
                if Redis is not connected or no suggestions are found.
        """
        if not self.redis:
            return []

        product_ids = [p.id for p in products]
        if len(products) == 1:
            suggestions = self.redis.zrange(
                self.get_product_key(product_ids[0]), 0, -1, desc=True,
            )[:max_results]
        else:
            flat_ids = "".join([str(product_id) for product_id in product_ids])
            tmp_key = f"tmp_{flat_ids}"
            keys = [self.get_product_key(product_id) for product_id in product_ids]
            self.redis.zunionstore(tmp_key, keys)
            self.redis.zrem(tmp_key, *product_ids)
            suggestions = self.redis.zrange(tmp_key, 0, -1, desc=True)[:max_results]
            self.redis.delete(tmp_key)

        suggested_ids = [int(suggestion_id) for suggestion_id in suggestions]
        products = list(Product.objects.filter(id__in=suggested_ids))
        products.sort(key=lambda x: suggested_ids.index(x.id))
        return products

    def clear_purchases(self):
        """
        Clears all recorded co-purchase data from Redis.

        This method iterates through all products and deletes their associated
        co-purchase sorted sets in Redis. This is useful for resetting the
        recommender data. This operation is skipped if the Redis connection
        is not established.
        """
        if not self.redis:
            return
        for product_id in Product.objects.values_list("id", flat=True):
            self.redis.delete(self.get_product_key(product_id))
