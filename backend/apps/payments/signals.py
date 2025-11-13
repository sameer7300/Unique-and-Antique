"""
Signals for the payments app.
"""

from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Payment, PaymentRefund


@receiver(post_save, sender=Payment)
def update_order_payment_status(sender, instance, **kwargs):
    """
    Update order payment status when payment status changes.
    """
    order = instance.order
    
    # Update order payment status based on payment status
    if instance.status == 'succeeded':
        order.payment_status = 'paid'
        # Auto-confirm order for successful payments (except COD)
        if instance.provider != 'cod' and order.status == 'pending':
            order.status = 'confirmed'
    elif instance.status == 'failed':
        order.payment_status = 'failed'
    elif instance.status == 'cancelled':
        order.payment_status = 'cancelled'
    elif instance.status == 'refunded':
        order.payment_status = 'refunded'
    
    order.save(update_fields=['payment_status', 'status'])


@receiver(post_save, sender=PaymentRefund)
def update_payment_refund_amount(sender, instance, created, **kwargs):
    """
    Update payment refunded amount when refund is processed.
    """
    if instance.status == 'succeeded':
        payment = instance.payment
        
        # Calculate total refunded amount
        total_refunded = payment.refunds.filter(
            status='succeeded'
        ).aggregate(
            total=models.Sum('amount')
        )['total'] or 0
        
        payment.refunded_amount = total_refunded
        
        # Update payment status
        if payment.refunded_amount >= payment.amount:
            payment.status = 'refunded'
        elif payment.refunded_amount > 0:
            payment.status = 'partially_refunded'
        
        payment.save(update_fields=['refunded_amount', 'status'])
