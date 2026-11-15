from django.core.cache import cache
from .models import Product

CACHE_TTL = 60 * 15

def get_products_by_category(category_id):
    cache_key = f'category_{category_id}'
    products = cache.get(cache_key)
    if products is None:
        products = list(Product.objects.filter(category_id=category_id).select_related('category'))
        cache.set(cache_key, products, timeout=CACHE_TTL)
    return products

def invalidate_category_cache(category_id):
    cache.delete(f'category_{category_id}')

def get_product_by_id(product_id):
    cache_key = f'product_{product_id}'
    product = cache.get(cache_key)
    if product is None:
        try:
            product = Product.objects.select_related('category', 'owner').get(pk=product_id)
            cache.set(cache_key, product, timeout=CACHE_TTL)
        except Product.DoesNotExist:
            return None
    return product

def invalidate_product_cache(product_id):
    cache.delete(f'product_{product_id}')