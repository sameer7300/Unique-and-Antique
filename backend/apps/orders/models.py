"""
Order models for the Unique and Antique E-commerce Platform.
"""

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator
from django.contrib.auth import get_user_model
from decimal import Decimal
import uuid

User = get_user_model()


class Order(models.Model):
    """
    Main Order model.
    """
    
    STATUS_CHOICES = [
        ('pending', _('Pending')),
        ('confirmed', _('Confirmed')),
        ('processing', _('Processing')),
        ('packed', _('Packed')),
        ('shipped', _('Shipped')),
        ('out_for_delivery', _('Out for Delivery')),
        ('delivered', _('Delivered')),
        ('cancelled', _('Cancelled')),
        ('returned', _('Returned')),
        ('refunded', _('Refunded')),
    ]
    
    PAYMENT_STATUS_CHOICES = [
        ('pending', _('Pending')),
        ('paid', _('Paid')),
        ('failed', _('Failed')),
        ('cancelled', _('Cancelled')),
        ('refunded', _('Refunded')),
        ('partially_refunded', _('Partially Refunded')),
    ]
    
    PAYMENT_METHOD_CHOICES = [
        ('stripe', _('Credit/Debit Card')),
        ('cod', _('Cash on Delivery')),
        ('paypal', _('PayPal')),
        ('bank_transfer', _('Bank Transfer')),
    ]
    
    # Order identification
    order_number = models.CharField(
        _('order number'),
        max_length=20,
        unique=True,
        editable=False
    )
    order_id = models.UUIDField(
        _('order ID'),
        default=uuid.uuid4,
        unique=True,
        editable=False
    )
    
    # Customer information
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='orders',
        verbose_name=_('customer')
    )
    
    # Order status
    status = models.CharField(
        _('order status'),
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    payment_status = models.CharField(
        _('payment status'),
        max_length=20,
        choices=PAYMENT_STATUS_CHOICES,
        default='pending'
    )
    payment_method = models.CharField(
        _('payment method'),
        max_length=20,
        choices=PAYMENT_METHOD_CHOICES
    )
    
    # Pricing information
    subtotal = models.DecimalField(
        _('subtotal'),
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    tax_amount = models.DecimalField(
        _('tax amount'),
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(0)]
    )
    shipping_cost = models.DecimalField(
        _('shipping cost'),
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(0)]
    )
    discount_amount = models.DecimalField(
        _('discount amount'),
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(0)]
    )
    total_amount = models.DecimalField(
        _('total amount'),
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    
    # Currency
    currency = models.CharField(
        _('currency'),
        max_length=3,
        default='PKR'
    )
    
    # Shipping information
    shipping_address = models.JSONField(
        _('shipping address'),
        help_text=_('Shipping address details as JSON')
    )
    billing_address = models.JSONField(
        _('billing address'),
        help_text=_('Billing address details as JSON')
    )
    
    # Shipping details
    shipping_method = models.CharField(
        _('shipping method'),
        max_length=100,
        blank=True
    )
    tracking_number = models.CharField(
        _('tracking number'),
        max_length=100,
        blank=True
    )
    carrier = models.CharField(
        _('carrier'),
        max_length=100,
        blank=True
    )
    
    # Order notes and metadata
    customer_notes = models.TextField(
        _('customer notes'),
        blank=True,
        help_text=_('Notes from customer')
    )
    admin_notes = models.TextField(
        _('admin notes'),
        blank=True,
        help_text=_('Internal notes for admin')
    )
    
    # Timestamps
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    confirmed_at = models.DateTimeField(_('confirmed at'), null=True, blank=True)
    shipped_at = models.DateTimeField(_('shipped at'), null=True, blank=True)
    delivered_at = models.DateTimeField(_('delivered at'), null=True, blank=True)
    
    # Estimated delivery
    estimated_delivery_date = models.DateTimeField(
        _('estimated delivery date'),
        null=True,
        blank=True
    )
    
    class Meta:
        db_table = 'orders_order'
        verbose_name = _('Order')
        verbose_name_plural = _('Orders')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['status', 'payment_status']),
            models.Index(fields=['order_number']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"Order {self.order_number}"
    
    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = self.generate_order_number()
        super().save(*args, **kwargs)
    
    def generate_order_number(self):
        """Generate unique order number."""
        import random
        import string
        from django.utils import timezone
        
        # Format: UA-YYYYMMDD-XXXX (UA = Unique Antique)
        date_str = timezone.now().strftime('%Y%m%d')
        random_str = ''.join(random.choices(string.digits, k=4))
        return f"UA-{date_str}-{random_str}"
    
    @property
    def total_items(self):
        """Get total number of items in order."""
        return self.items.aggregate(
            total=models.Sum('quantity')
        )['total'] or 0
    
    @property
    def can_be_cancelled(self):
        """Check if order can be cancelled."""
        return self.status in ['pending', 'confirmed', 'processing']
    
    @property
    def can_be_returned(self):
        """Check if order can be returned."""
        return self.status == 'delivered'
    
    @property
    def is_paid(self):
        """Check if order is paid."""
        return self.payment_status == 'paid'
    
    @property
    def is_completed(self):
        """Check if order is completed."""
        return self.status == 'delivered'
    
    def calculate_total(self):
        """Calculate and update order total."""
        self.total_amount = (
            self.subtotal + 
            self.tax_amount + 
            self.shipping_cost - 
            self.discount_amount
        )
        return self.total_amount


class OrderItem(models.Model):
    """
    Individual items in an order.
    """
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name=_('order')
    )
    product = models.ForeignKey(
        'products.Product',
        on_delete=models.CASCADE,
        related_name='order_items',
        verbose_name=_('product')
    )
    variant = models.ForeignKey(
        'products.ProductVariant',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='order_items',
        verbose_name=_('product variant')
    )
    
    # Product details at time of order (for historical record)
    product_name = models.CharField(_('product name'), max_length=200)
    product_sku = models.CharField(_('product SKU'), max_length=100)
    variant_name = models.CharField(
        _('variant name'),
        max_length=100,
        blank=True
    )
    
    # Pricing and quantity
    quantity = models.PositiveIntegerField(
        _('quantity'),
        validators=[MinValueValidator(1)]
    )
    unit_price = models.DecimalField(
        _('unit price'),
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    total_price = models.DecimalField(
        _('total price'),
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    
    # Additional options/customizations
    options = models.JSONField(
        _('item options'),
        default=dict,
        blank=True,
        help_text=_('Item options or customizations')
    )
    
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    
    class Meta:
        db_table = 'orders_orderitem'
        verbose_name = _('Order Item')
        verbose_name_plural = _('Order Items')
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['order', 'product']),
        ]
    
    def __str__(self):
        variant_info = f" ({self.variant_name})" if self.variant_name else ""
        return f"{self.product_name}{variant_info} x {self.quantity}"
    
    def save(self, *args, **kwargs):
        # Set product details for historical record
        if not self.product_name:
            self.product_name = self.product.title
        if not self.product_sku:
            self.product_sku = self.variant.sku if self.variant else self.product.sku
        if self.variant and not self.variant_name:
            self.variant_name = self.variant.name
        
        # Calculate total price
        self.total_price = self.unit_price * self.quantity
        
        super().save(*args, **kwargs)


class OrderStatusHistory(models.Model):
    """
    Track order status changes.
    """
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='status_history',
        verbose_name=_('order')
    )
    status = models.CharField(
        _('status'),
        max_length=20,
        choices=Order.STATUS_CHOICES
    )
    notes = models.TextField(
        _('notes'),
        blank=True,
        help_text=_('Additional notes about status change')
    )
    changed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='order_status_changes',
        verbose_name=_('changed by')
    )
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    
    class Meta:
        db_table = 'orders_orderstatushistory'
        verbose_name = _('Order Status History')
        verbose_name_plural = _('Order Status Histories')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['order', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.order.order_number} - {self.get_status_display()}"


class OrderShipment(models.Model):
    """
    Order shipment tracking information.
    """
    
    STATUS_CHOICES = [
        ('pending', _('Pending')),
        ('picked_up', _('Picked Up')),
        ('in_transit', _('In Transit')),
        ('out_for_delivery', _('Out for Delivery')),
        ('delivered', _('Delivered')),
        ('failed_delivery', _('Failed Delivery')),
        ('returned', _('Returned')),
    ]
    
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='shipments',
        verbose_name=_('order')
    )
    
    # Shipment details
    tracking_number = models.CharField(
        _('tracking number'),
        max_length=100,
        unique=True
    )
    carrier = models.CharField(_('carrier'), max_length=100)
    service_type = models.CharField(
        _('service type'),
        max_length=100,
        blank=True,
        help_text=_('Express, Standard, etc.')
    )
    
    # Status and tracking
    status = models.CharField(
        _('shipment status'),
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    
    # Addresses
    origin_address = models.JSONField(
        _('origin address'),
        help_text=_('Warehouse/origin address')
    )
    destination_address = models.JSONField(
        _('destination address'),
        help_text=_('Customer delivery address')
    )
    
    # Timestamps
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    shipped_at = models.DateTimeField(_('shipped at'), null=True, blank=True)
    estimated_delivery = models.DateTimeField(
        _('estimated delivery'),
        null=True,
        blank=True
    )
    delivered_at = models.DateTimeField(_('delivered at'), null=True, blank=True)
    
    # Additional information
    weight = models.DecimalField(
        _('weight (kg)'),
        max_digits=8,
        decimal_places=3,
        null=True,
        blank=True
    )
    dimensions = models.JSONField(
        _('dimensions'),
        default=dict,
        blank=True,
        help_text=_('Package dimensions (length, width, height)')
    )
    
    class Meta:
        db_table = 'orders_ordershipment'
        verbose_name = _('Order Shipment')
        verbose_name_plural = _('Order Shipments')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['tracking_number']),
            models.Index(fields=['order', 'status']),
        ]
    
    def __str__(self):
        return f"Shipment {self.tracking_number} for {self.order.order_number}"


class OrderReturn(models.Model):
    """
    Order return/refund requests.
    """
    
    STATUS_CHOICES = [
        ('requested', _('Requested')),
        ('approved', _('Approved')),
        ('rejected', _('Rejected')),
        ('received', _('Received')),
        ('processed', _('Processed')),
        ('refunded', _('Refunded')),
    ]
    
    REASON_CHOICES = [
        ('defective', _('Defective Product')),
        ('wrong_item', _('Wrong Item Received')),
        ('not_as_described', _('Not as Described')),
        ('damaged_shipping', _('Damaged in Shipping')),
        ('changed_mind', _('Changed Mind')),
        ('size_fit', _('Size/Fit Issues')),
        ('other', _('Other')),
    ]
    
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='returns',
        verbose_name=_('order')
    )
    
    # Return details
    return_number = models.CharField(
        _('return number'),
        max_length=20,
        unique=True,
        editable=False
    )
    status = models.CharField(
        _('return status'),
        max_length=20,
        choices=STATUS_CHOICES,
        default='requested'
    )
    reason = models.CharField(
        _('return reason'),
        max_length=20,
        choices=REASON_CHOICES
    )
    
    # Return information
    customer_notes = models.TextField(
        _('customer notes'),
        help_text=_('Customer explanation for return')
    )
    admin_notes = models.TextField(
        _('admin notes'),
        blank=True,
        help_text=_('Internal admin notes')
    )
    
    # Refund information
    refund_amount = models.DecimalField(
        _('refund amount'),
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)]
    )
    
    # Timestamps
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    approved_at = models.DateTimeField(_('approved at'), null=True, blank=True)
    processed_at = models.DateTimeField(_('processed at'), null=True, blank=True)
    
    class Meta:
        db_table = 'orders_orderreturn'
        verbose_name = _('Order Return')
        verbose_name_plural = _('Order Returns')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['order', 'status']),
            models.Index(fields=['return_number']),
        ]
    
    def __str__(self):
        return f"Return {self.return_number} for {self.order.order_number}"
    
    def save(self, *args, **kwargs):
        if not self.return_number:
            self.return_number = self.generate_return_number()
        super().save(*args, **kwargs)
    
    def generate_return_number(self):
        """Generate unique return number."""
        import random
        import string
        from django.utils import timezone
        
        # Format: RT-YYYYMMDD-XXXX
        date_str = timezone.now().strftime('%Y%m%d')
        random_str = ''.join(random.choices(string.digits, k=4))
        return f"RT-{date_str}-{random_str}"


class OrderReturnItem(models.Model):
    """
    Individual items in a return request.
    """
    return_request = models.ForeignKey(
        OrderReturn,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name=_('return request')
    )
    order_item = models.ForeignKey(
        OrderItem,
        on_delete=models.CASCADE,
        related_name='return_items',
        verbose_name=_('order item')
    )
    quantity = models.PositiveIntegerField(
        _('return quantity'),
        validators=[MinValueValidator(1)]
    )
    condition = models.CharField(
        _('item condition'),
        max_length=100,
        blank=True,
        help_text=_('Condition of returned item')
    )
    
    class Meta:
        db_table = 'orders_orderreturnitem'
        verbose_name = _('Order Return Item')
        verbose_name_plural = _('Order Return Items')
        unique_together = ['return_request', 'order_item']
    
    def __str__(self):
        return f"Return {self.order_item.product_name} x {self.quantity}"
