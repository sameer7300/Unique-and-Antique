"""
Signals for the products app.
"""

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Product, ProductImage


@receiver(post_save, sender=ProductImage)
def set_primary_image(sender, instance, created, **kwargs):
    """
    Ensure only one primary image per product and set first image as primary if none exists.
    """
    if instance.is_primary:
        # Ensure only one primary image per product
        ProductImage.objects.filter(
            product=instance.product,
            is_primary=True
        ).exclude(pk=instance.pk).update(is_primary=False)
    else:
        # If no primary image exists, make this one primary
        if not ProductImage.objects.filter(
            product=instance.product,
            is_primary=True
        ).exists():
            instance.is_primary = True
            instance.save(update_fields=['is_primary'])


@receiver(post_delete, sender=ProductImage)
def reassign_primary_image(sender, instance, **kwargs):
    """
    Reassign primary image if the current primary image is deleted.
    """
    if instance.is_primary:
        # Find the next image to make primary
        next_image = ProductImage.objects.filter(
            product=instance.product
        ).first()
        
        if next_image:
            next_image.is_primary = True
            next_image.save(update_fields=['is_primary'])


@receiver(post_save, sender=Product)
def update_product_search_vector(sender, instance, **kwargs):
    """
    Update search vector when product is saved (for full-text search).
    This would be used with PostgreSQL full-text search.
    """
    # This is a placeholder for search vector updates
    # In a real implementation, you might update a search vector field
    # or trigger a search index update (Elasticsearch, etc.)
    pass
