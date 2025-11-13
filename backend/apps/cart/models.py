"""
Shopping Cart models for the Unique and Antique E-commerce Platform.
"""

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator
from django.contrib.auth import get_user_model
from decimal import Decimal
import uuid

User = get_user_model()


class Cart(models.Model):
    """
    Shopping Cart model to group cart items.
    """
    
    STATUS_CHOICES = [
        ('active', _('Active')),
        ('abandoned', _('Abandoned')),
        ('converted', _('Converted to Order')),
        ('expired', _('Expired')),
    ]
    
    # User association (null for guest carts)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='carts',
        verbose_name=_('user')
    )
    
    # Session ID for guest carts
    session_key = models.CharField(
        _('session key'),
        max_length=40,
        null=True,
        blank=True,
        help_text=_('Session ID for guest users')
    )
    
    # Cart identification
    cart_id = models.UUIDField(
        _('cart ID'),
        default=uuid.uuid4,
        unique=True,
        editable=False
    )
    
    # Cart status and metadata
    status = models.CharField(
        _('status'),
        max_length=20,
        choices=STATUS_CHOICES,
        default='active'
    )
    
    # Timestamps
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    expires_at = models.DateTimeField(
        _('expires at'),
        null=True,
        blank=True,
        help_text=_('When the cart expires for cleanup')
    )
    
    # Conversion tracking
    converted_to_order = models.ForeignKey(
        'orders.Order',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='source_cart',
        verbose_name=_('converted to order')
    )
    
    class Meta:
        db_table = 'cart_cart'
        verbose_name = _('Cart')
        verbose_name_plural = _('Carts')
        ordering = ['-updated_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['session_key', 'status']),
            models.Index(fields=['expires_at']),
        ]
    
    def __str__(self):
        if self.user:
            return f"Cart for {self.user.email}"
        return f"Guest Cart {self.cart_id}"
    
    @property
    def total_items(self):
        """Get total number of items in cart."""
        return self.items.aggregate(
            total=models.Sum('quantity')
        )['total'] or 0
    
    @property
    def subtotal(self):
        """Calculate cart subtotal."""
        return sum(item.total_price for item in self.items.all())
    
    @property
    def total_weight(self):
        """Calculate total weight of cart items."""
        total = Decimal('0.00')
        for item in self.items.all():
            if item.product.weight:
                total += item.product.weight * item.quantity
        return total
    
    @property
    def is_empty(self):
        """Check if cart is empty."""
        return not self.items.exists()
    
    def clear(self):
        """Clear all items from cart."""
        self.items.all().delete()
        self.save()
    
    def add_item(self, product, quantity=1, variant=None):
        """Add item to cart or update quantity if exists."""
        cart_item, created = CartItem.objects.get_or_create(
            cart=self,
            product=product,
            variant=variant,
            defaults={'quantity': quantity}
        )
        
        if not created:
            cart_item.quantity += quantity
            cart_item.save()
        
        return cart_item
    
    def remove_item(self, product, variant=None):
        """Remove item from cart."""
        try:
            item = self.items.get(product=product, variant=variant)
            item.delete()
        except CartItem.DoesNotExist:
            pass
    
    def update_item_quantity(self, product, quantity, variant=None):
        """Update item quantity in cart."""
        try:
            item = self.items.get(product=product, variant=variant)
            if quantity <= 0:
                item.delete()
            else:
                item.quantity = quantity
                item.save()
        except CartItem.DoesNotExist:
            if quantity > 0:
                self.add_item(product, quantity, variant)


class CartItem(models.Model):
    """
    Individual items in a shopping cart.
    """
    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name=_('cart')
    )
    product = models.ForeignKey(
        'products.Product',
        on_delete=models.CASCADE,
        related_name='cart_items',
        verbose_name=_('product')
    )
    variant = models.ForeignKey(
        'products.ProductVariant',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='cart_items',
        verbose_name=_('product variant')
    )
    quantity = models.PositiveIntegerField(
        _('quantity'),
        default=1,
        validators=[MinValueValidator(1)]
    )
    
    # Price at the time of adding to cart
    price_at_add = models.DecimalField(
        _('price when added'),
        max_digits=10,
        decimal_places=2,
        help_text=_('Price when item was added to cart')
    )
    
    # Additional options/customizations
    options = models.JSONField(
        _('item options'),
        default=dict,
        blank=True,
        help_text=_('Additional item options or customizations')
    )
    
    # Timestamps
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        db_table = 'cart_cartitem'
        verbose_name = _('Cart Item')
        verbose_name_plural = _('Cart Items')
        ordering = ['-created_at']
        unique_together = ['cart', 'product', 'variant']
        indexes = [
            models.Index(fields=['cart', 'product']),
        ]
    
    def __str__(self):
        variant_info = f" ({self.variant.name})" if self.variant else ""
        return f"{self.product.title}{variant_info} x {self.quantity}"
    
    def save(self, *args, **kwargs):
        # Set price_at_add if not provided
        if not self.price_at_add:
            if self.variant:
                self.price_at_add = self.variant.price
            else:
                self.price_at_add = self.product.price
        super().save(*args, **kwargs)
    
    @property
    def current_price(self):
        """Get current price of the product/variant."""
        if self.variant:
            return self.variant.price
        return self.product.price
    
    @property
    def total_price(self):
        """Calculate total price for this cart item."""
        return self.price_at_add * self.quantity
    
    @property
    def price_changed(self):
        """Check if price has changed since adding to cart."""
        return self.price_at_add != self.current_price
    
    @property
    def is_available(self):
        """Check if item is still available."""
        if self.variant:
            return self.variant.is_active and self.variant.is_in_stock
        return (
            self.product.status == 'active' and 
            self.product.is_in_stock
        )
    
    @property
    def stock_available(self):
        """Get available stock for this item."""
        if self.variant:
            return self.variant.stock
        return self.product.stock if self.product.track_inventory else float('inf')
    
    @property
    def can_fulfill_quantity(self):
        """Check if requested quantity can be fulfilled."""
        if not self.is_available:
            return False
        
        available_stock = self.stock_available
        if available_stock == float('inf'):  # Unlimited stock
            return True
        
        return self.quantity <= available_stock


class SavedItem(models.Model):
    """
    Saved items (wishlist) for users.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='saved_items',
        verbose_name=_('user')
    )
    product = models.ForeignKey(
        'products.Product',
        on_delete=models.CASCADE,
        related_name='saved_by_users',
        verbose_name=_('product')
    )
    variant = models.ForeignKey(
        'products.ProductVariant',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='saved_by_users',
        verbose_name=_('product variant')
    )
    
    # Notes or comments about the saved item
    notes = models.TextField(
        _('notes'),
        blank=True,
        help_text=_('Personal notes about this saved item')
    )
    
    # Timestamps
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        db_table = 'cart_saveditem'
        verbose_name = _('Saved Item')
        verbose_name_plural = _('Saved Items')
        ordering = ['-created_at']
        unique_together = ['user', 'product', 'variant']
        indexes = [
            models.Index(fields=['user', 'created_at']),
        ]
    
    def __str__(self):
        variant_info = f" ({self.variant.name})" if self.variant else ""
        return f"{self.user.email} saved {self.product.title}{variant_info}"
    
    def move_to_cart(self, quantity=1):
        """Move saved item to cart."""
        # Get or create active cart for user
        cart, created = Cart.objects.get_or_create(
            user=self.user,
            status='active',
            defaults={'expires_at': None}
        )
        
        # Add item to cart
        cart_item = cart.add_item(
            product=self.product,
            quantity=quantity,
            variant=self.variant
        )
        
        return cart_item


class CartCoupon(models.Model):
    """
    Applied coupons to carts.
    """
    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name='applied_coupons',
        verbose_name=_('cart')
    )
    coupon_code = models.CharField(_('coupon code'), max_length=50)
    discount_amount = models.DecimalField(
        _('discount amount'),
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    discount_type = models.CharField(
        _('discount type'),
        max_length=20,
        choices=[
            ('fixed', _('Fixed Amount')),
            ('percentage', _('Percentage')),
        ]
    )
    applied_at = models.DateTimeField(_('applied at'), auto_now_add=True)
    
    class Meta:
        db_table = 'cart_cartcoupon'
        verbose_name = _('Cart Coupon')
        verbose_name_plural = _('Cart Coupons')
        unique_together = ['cart', 'coupon_code']
    
    def __str__(self):
        return f"{self.coupon_code} applied to {self.cart}"
