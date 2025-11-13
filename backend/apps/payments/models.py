"""
Payment models for the Unique and Antique E-commerce Platform.
"""

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator
from django.contrib.auth import get_user_model
from decimal import Decimal
import uuid

User = get_user_model()


class Payment(models.Model):
    """
    Main Payment model to track all payment transactions.
    """
    
    STATUS_CHOICES = [
        ('pending', _('Pending')),
        ('processing', _('Processing')),
        ('succeeded', _('Succeeded')),
        ('failed', _('Failed')),
        ('cancelled', _('Cancelled')),
        ('refunded', _('Refunded')),
        ('partially_refunded', _('Partially Refunded')),
    ]
    
    PROVIDER_CHOICES = [
        ('stripe', _('Stripe')),
        ('paypal', _('PayPal')),
        ('cod', _('Cash on Delivery')),
        ('bank_transfer', _('Bank Transfer')),
        ('wallet', _('Digital Wallet')),
    ]
    
    PAYMENT_TYPE_CHOICES = [
        ('payment', _('Payment')),
        ('refund', _('Refund')),
        ('partial_refund', _('Partial Refund')),
    ]
    
    # Payment identification
    payment_id = models.UUIDField(
        _('payment ID'),
        default=uuid.uuid4,
        unique=True,
        editable=False
    )
    
    # Related order
    order = models.ForeignKey(
        'orders.Order',
        on_delete=models.CASCADE,
        related_name='payments',
        verbose_name=_('order')
    )
    
    # Payment details
    provider = models.CharField(
        _('payment provider'),
        max_length=20,
        choices=PROVIDER_CHOICES
    )
    provider_payment_id = models.CharField(
        _('provider payment ID'),
        max_length=255,
        blank=True,
        help_text=_('Payment ID from payment provider')
    )
    provider_payment_intent_id = models.CharField(
        _('provider payment intent ID'),
        max_length=255,
        blank=True,
        help_text=_('Payment intent ID from provider (Stripe)')
    )
    
    # Payment status and type
    status = models.CharField(
        _('payment status'),
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    payment_type = models.CharField(
        _('payment type'),
        max_length=20,
        choices=PAYMENT_TYPE_CHOICES,
        default='payment'
    )
    
    # Amount information
    amount = models.DecimalField(
        _('amount'),
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    currency = models.CharField(
        _('currency'),
        max_length=3,
        default='USD'
    )
    
    # Fee information
    processing_fee = models.DecimalField(
        _('processing fee'),
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(0)]
    )
    
    # Payment method details
    payment_method_details = models.JSONField(
        _('payment method details'),
        default=dict,
        blank=True,
        help_text=_('Details about payment method (card last 4, etc.)')
    )
    
    # Billing information
    billing_address = models.JSONField(
        _('billing address'),
        default=dict,
        blank=True,
        help_text=_('Billing address for this payment')
    )
    
    # Metadata and notes
    metadata = models.JSONField(
        _('metadata'),
        default=dict,
        blank=True,
        help_text=_('Additional payment metadata')
    )
    failure_reason = models.TextField(
        _('failure reason'),
        blank=True,
        help_text=_('Reason for payment failure')
    )
    admin_notes = models.TextField(
        _('admin notes'),
        blank=True,
        help_text=_('Internal admin notes')
    )
    
    # Timestamps
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    processed_at = models.DateTimeField(_('processed at'), null=True, blank=True)
    
    # Refund information
    refunded_amount = models.DecimalField(
        _('refunded amount'),
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(0)]
    )
    
    class Meta:
        db_table = 'payments_payment'
        verbose_name = _('Payment')
        verbose_name_plural = _('Payments')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['order', 'status']),
            models.Index(fields=['provider', 'status']),
            models.Index(fields=['provider_payment_id']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"Payment {self.payment_id} - {self.order.order_number}"
    
    @property
    def is_successful(self):
        """Check if payment is successful."""
        return self.status == 'succeeded'
    
    @property
    def is_refundable(self):
        """Check if payment can be refunded."""
        return (
            self.status == 'succeeded' and 
            self.refunded_amount < self.amount
        )
    
    @property
    def remaining_refundable_amount(self):
        """Get remaining amount that can be refunded."""
        if not self.is_refundable:
            return Decimal('0.00')
        return self.amount - self.refunded_amount
    
    def create_refund(self, amount, reason=''):
        """Create a refund for this payment."""
        if not self.is_refundable:
            raise ValueError("Payment is not refundable")
        
        if amount > self.remaining_refundable_amount:
            raise ValueError("Refund amount exceeds refundable amount")
        
        refund = PaymentRefund.objects.create(
            payment=self,
            amount=amount,
            reason=reason,
            status='pending'
        )
        
        return refund


class PaymentRefund(models.Model):
    """
    Payment refund tracking.
    """
    
    STATUS_CHOICES = [
        ('pending', _('Pending')),
        ('processing', _('Processing')),
        ('succeeded', _('Succeeded')),
        ('failed', _('Failed')),
        ('cancelled', _('Cancelled')),
    ]
    
    # Related payment
    payment = models.ForeignKey(
        Payment,
        on_delete=models.CASCADE,
        related_name='refunds',
        verbose_name=_('payment')
    )
    
    # Refund identification
    refund_id = models.UUIDField(
        _('refund ID'),
        default=uuid.uuid4,
        unique=True,
        editable=False
    )
    provider_refund_id = models.CharField(
        _('provider refund ID'),
        max_length=255,
        blank=True,
        help_text=_('Refund ID from payment provider')
    )
    
    # Refund details
    amount = models.DecimalField(
        _('refund amount'),
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    currency = models.CharField(
        _('currency'),
        max_length=3,
        default='USD'
    )
    status = models.CharField(
        _('refund status'),
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    
    # Refund reason and notes
    reason = models.CharField(
        _('refund reason'),
        max_length=255,
        blank=True
    )
    admin_notes = models.TextField(
        _('admin notes'),
        blank=True
    )
    
    # Metadata
    metadata = models.JSONField(
        _('metadata'),
        default=dict,
        blank=True
    )
    
    # Timestamps
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    processed_at = models.DateTimeField(_('processed at'), null=True, blank=True)
    
    class Meta:
        db_table = 'payments_paymentrefund'
        verbose_name = _('Payment Refund')
        verbose_name_plural = _('Payment Refunds')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['payment', 'status']),
            models.Index(fields=['provider_refund_id']),
        ]
    
    def __str__(self):
        return f"Refund {self.refund_id} - {self.amount} {self.currency}"


class PaymentMethod(models.Model):
    """
    Saved payment methods for users.
    """
    
    TYPE_CHOICES = [
        ('card', _('Credit/Debit Card')),
        ('bank_account', _('Bank Account')),
        ('digital_wallet', _('Digital Wallet')),
    ]
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='payment_methods',
        verbose_name=_('user')
    )
    
    # Payment method details
    type = models.CharField(
        _('payment method type'),
        max_length=20,
        choices=TYPE_CHOICES
    )
    provider = models.CharField(
        _('provider'),
        max_length=20,
        choices=Payment.PROVIDER_CHOICES
    )
    provider_payment_method_id = models.CharField(
        _('provider payment method ID'),
        max_length=255,
        help_text=_('Payment method ID from provider')
    )
    
    # Display information
    display_name = models.CharField(
        _('display name'),
        max_length=100,
        help_text=_('User-friendly name for payment method')
    )
    last_four = models.CharField(
        _('last four digits'),
        max_length=4,
        blank=True,
        help_text=_('Last 4 digits of card/account')
    )
    brand = models.CharField(
        _('brand'),
        max_length=50,
        blank=True,
        help_text=_('Card brand (Visa, Mastercard, etc.)')
    )
    
    # Status and settings
    is_default = models.BooleanField(_('is default'), default=False)
    is_active = models.BooleanField(_('is active'), default=True)
    
    # Expiration (for cards)
    expires_month = models.PositiveIntegerField(
        _('expiration month'),
        null=True,
        blank=True
    )
    expires_year = models.PositiveIntegerField(
        _('expiration year'),
        null=True,
        blank=True
    )
    
    # Metadata
    metadata = models.JSONField(
        _('metadata'),
        default=dict,
        blank=True
    )
    
    # Timestamps
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        db_table = 'payments_paymentmethod'
        verbose_name = _('Payment Method')
        verbose_name_plural = _('Payment Methods')
        ordering = ['-is_default', '-created_at']
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['provider_payment_method_id']),
        ]
    
    def __str__(self):
        return f"{self.display_name} ({self.user.email})"
    
    def save(self, *args, **kwargs):
        # Ensure only one default payment method per user
        if self.is_default:
            PaymentMethod.objects.filter(
                user=self.user,
                is_default=True
            ).exclude(pk=self.pk).update(is_default=False)
        
        super().save(*args, **kwargs)


class PaymentWebhook(models.Model):
    """
    Track payment webhook events from providers.
    """
    
    STATUS_CHOICES = [
        ('pending', _('Pending')),
        ('processed', _('Processed')),
        ('failed', _('Failed')),
        ('ignored', _('Ignored')),
    ]
    
    # Webhook identification
    webhook_id = models.UUIDField(
        _('webhook ID'),
        default=uuid.uuid4,
        unique=True,
        editable=False
    )
    provider = models.CharField(
        _('provider'),
        max_length=20,
        choices=Payment.PROVIDER_CHOICES
    )
    provider_webhook_id = models.CharField(
        _('provider webhook ID'),
        max_length=255,
        blank=True
    )
    
    # Event details
    event_type = models.CharField(
        _('event type'),
        max_length=100,
        help_text=_('Type of webhook event')
    )
    event_data = models.JSONField(
        _('event data'),
        help_text=_('Full webhook event data')
    )
    
    # Processing status
    status = models.CharField(
        _('processing status'),
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    processing_notes = models.TextField(
        _('processing notes'),
        blank=True,
        help_text=_('Notes about webhook processing')
    )
    
    # Related objects
    related_payment = models.ForeignKey(
        Payment,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='webhooks',
        verbose_name=_('related payment')
    )
    
    # Timestamps
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    processed_at = models.DateTimeField(_('processed at'), null=True, blank=True)
    
    class Meta:
        db_table = 'payments_paymentwebhook'
        verbose_name = _('Payment Webhook')
        verbose_name_plural = _('Payment Webhooks')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['provider', 'event_type']),
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['provider_webhook_id']),
        ]
    
    def __str__(self):
        return f"{self.provider} webhook - {self.event_type}"


class PaymentTransaction(models.Model):
    """
    Detailed transaction log for payments.
    """
    
    ACTION_CHOICES = [
        ('authorize', _('Authorize')),
        ('capture', _('Capture')),
        ('charge', _('Charge')),
        ('refund', _('Refund')),
        ('void', _('Void')),
        ('cancel', _('Cancel')),
    ]
    
    STATUS_CHOICES = [
        ('pending', _('Pending')),
        ('succeeded', _('Succeeded')),
        ('failed', _('Failed')),
    ]
    
    # Related payment
    payment = models.ForeignKey(
        Payment,
        on_delete=models.CASCADE,
        related_name='transactions',
        verbose_name=_('payment')
    )
    
    # Transaction details
    transaction_id = models.UUIDField(
        _('transaction ID'),
        default=uuid.uuid4,
        unique=True,
        editable=False
    )
    provider_transaction_id = models.CharField(
        _('provider transaction ID'),
        max_length=255,
        blank=True
    )
    
    # Action and status
    action = models.CharField(
        _('action'),
        max_length=20,
        choices=ACTION_CHOICES
    )
    status = models.CharField(
        _('status'),
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    
    # Amount
    amount = models.DecimalField(
        _('amount'),
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    currency = models.CharField(
        _('currency'),
        max_length=3,
        default='USD'
    )
    
    # Response and error details
    response_data = models.JSONField(
        _('response data'),
        default=dict,
        blank=True,
        help_text=_('Response data from payment provider')
    )
    error_message = models.TextField(
        _('error message'),
        blank=True
    )
    
    # Timestamps
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    processed_at = models.DateTimeField(_('processed at'), null=True, blank=True)
    
    class Meta:
        db_table = 'payments_paymenttransaction'
        verbose_name = _('Payment Transaction')
        verbose_name_plural = _('Payment Transactions')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['payment', 'action']),
            models.Index(fields=['status', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.action} - {self.amount} {self.currency}"
