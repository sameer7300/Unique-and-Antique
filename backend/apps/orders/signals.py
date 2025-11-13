"""
Signals for the orders app.
"""

from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone
from .models import Order, OrderStatusHistory
from .services import OrderEmailService
import logging

logger = logging.getLogger(__name__)


@receiver(pre_save, sender=Order)
def track_order_status_changes(sender, instance, **kwargs):
    """
    Track order status changes and update timestamps.
    """
    if instance.pk:
        try:
            old_instance = Order.objects.get(pk=instance.pk)
            
            # Track status changes
            if old_instance.status != instance.status:
                # Update status-specific timestamps
                if instance.status == 'confirmed' and not instance.confirmed_at:
                    instance.confirmed_at = timezone.now()
                elif instance.status == 'shipped' and not instance.shipped_at:
                    instance.shipped_at = timezone.now()
                elif instance.status == 'delivered' and not instance.delivered_at:
                    instance.delivered_at = timezone.now()
                
                # Create status history entry (will be created in post_save)
                instance._status_changed = True
                instance._old_status = old_instance.status
            else:
                instance._status_changed = False
                
        except Order.DoesNotExist:
            instance._status_changed = False


@receiver(post_save, sender=Order)
def create_order_status_history(sender, instance, created, **kwargs):
    """
    Create order status history entry when order status changes.
    """
    if created:
        # Create initial status history entry
        OrderStatusHistory.objects.create(
            order=instance,
            status=instance.status,
            notes=f"Order created with status: {instance.get_status_display()}"
        )
        
        # Send order confirmation emails for new orders (only if not sent via API)
        # Check if this order creation is coming from API (which already sends emails)
        if not getattr(instance, '_skip_confirmation_email', False):
            try:
                logger.info(f"Sending order confirmation emails for new order {instance.order_number}")
                email_result = OrderEmailService.send_order_confirmation_email(instance)
                if email_result.get('customer_email_sent'):
                    logger.info(f"Order confirmation email sent successfully for order {instance.order_number}")
                else:
                    logger.warning(f"Failed to send order confirmation email for order {instance.order_number}")
            except Exception as e:
                logger.error(f"Error sending order confirmation emails for order {instance.order_number}: {str(e)}")
            
    elif getattr(instance, '_status_changed', False):
        # Create status change history entry
        OrderStatusHistory.objects.create(
            order=instance,
            status=instance.status,
            notes=f"Status changed from {instance._old_status} to {instance.status}"
        )
        
        # Send status change emails (only if not sent via API)
        if not getattr(instance, '_skip_status_email', False):
            try:
                old_status = instance._old_status
                new_status = instance.status
                logger.info(f"Sending status change emails for order {instance.order_number}: {old_status} -> {new_status}")
                
                email_result = OrderEmailService.send_order_status_change_email(
                    instance, old_status, new_status, changed_by=None
                )
                
                if email_result.get('customer_email_sent'):
                    logger.info(f"Status change email sent successfully to customer for order {instance.order_number}")
                else:
                    logger.warning(f"Failed to send status change email to customer for order {instance.order_number}")
                    
                if email_result.get('admin_email_sent'):
                    logger.info(f"Status change email sent successfully to admin for order {instance.order_number}")
                else:
                    logger.warning(f"Failed to send status change email to admin for order {instance.order_number}")
                    
            except Exception as e:
                logger.error(f"Error sending status change emails for order {instance.order_number}: {str(e)}")
        else:
            logger.info(f"Skipping status change emails for order {instance.order_number} (handled by API)")


@receiver(post_save, sender=Order)
def update_inventory_on_order_confirmation(sender, instance, **kwargs):
    """
    Update product inventory when order is confirmed.
    """
    if instance.status == 'confirmed' and instance.payment_status == 'paid':
        for item in instance.items.all():
            product = item.product
            variant = item.variant
            
            if variant:
                # Update variant stock
                if variant.stock >= item.quantity:
                    variant.stock -= item.quantity
                    variant.save(update_fields=['stock'])
            else:
                # Update product stock
                if product.track_inventory and product.stock >= item.quantity:
                    product.stock -= item.quantity
                    product.save(update_fields=['stock'])
