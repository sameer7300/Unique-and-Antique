"""
Signals for the cart app.
"""

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils import timezone
from datetime import timedelta
from .models import Cart, CartItem


@receiver(post_save, sender=CartItem)
def update_cart_timestamp(sender, instance, **kwargs):
    """
    Update cart timestamp when cart item is saved.
    """
    instance.cart.save(update_fields=['updated_at'])


@receiver(post_delete, sender=CartItem)
def update_cart_on_item_delete(sender, instance, **kwargs):
    """
    Update cart timestamp when cart item is deleted.
    """
    if instance.cart_id:  # Check if cart still exists
        try:
            instance.cart.save(update_fields=['updated_at'])
        except Cart.DoesNotExist:
            pass


@receiver(post_save, sender=Cart)
def set_cart_expiration(sender, instance, created, **kwargs):
    """
    Set cart expiration time for guest carts.
    """
    if created and not instance.user and not instance.expires_at:
        # Set expiration to 30 days for guest carts
        instance.expires_at = timezone.now() + timedelta(days=30)
        instance.save(update_fields=['expires_at'])
