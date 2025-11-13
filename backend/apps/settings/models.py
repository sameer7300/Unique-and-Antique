"""
Models for site settings and configuration.
"""

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal


class SiteSettings(models.Model):
    """
    Site-wide settings that can be configured by admin.
    Singleton model - only one instance should exist.
    """
    
    # Tax Settings
    tax_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('8.25'),
        validators=[MinValueValidator(Decimal('0')), MaxValueValidator(Decimal('100'))],
        help_text="Tax rate as percentage (e.g., 8.25 for 8.25%)"
    )
    tax_enabled = models.BooleanField(
        default=True,
        help_text="Enable/disable tax calculation"
    )
    
    # Shipping Settings
    free_shipping_threshold = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('25000.00'),
        validators=[MinValueValidator(Decimal('0'))],
        help_text="Minimum order amount for free shipping (PKR)"
    )
    standard_shipping_cost = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=Decimal('500.00'),
        validators=[MinValueValidator(Decimal('0'))],
        help_text="Standard shipping cost (PKR)"
    )
    express_shipping_cost = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=Decimal('1000.00'),
        validators=[MinValueValidator(Decimal('0'))],
        help_text="Express shipping cost (PKR)"
    )
    shipping_enabled = models.BooleanField(
        default=True,
        help_text="Enable/disable shipping cost calculation"
    )
    
    # Currency Settings
    currency_code = models.CharField(
        max_length=3,
        default='PKR',
        help_text="Currency code (e.g., PKR, USD)"
    )
    currency_symbol = models.CharField(
        max_length=10,
        default='PKR',
        help_text="Currency symbol to display"
    )
    
    # Order Settings
    minimum_order_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('100.00'),
        validators=[MinValueValidator(Decimal('0'))],
        help_text="Minimum order amount (PKR)"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Site Settings"
        verbose_name_plural = "Site Settings"
    
    def __str__(self):
        return f"Site Settings (Tax: {self.tax_rate}%, Shipping: {self.currency_symbol} {self.standard_shipping_cost})"
    
    def save(self, *args, **kwargs):
        """Ensure only one instance exists (singleton pattern)."""
        if not self.pk and SiteSettings.objects.exists():
            # If this is a new instance and one already exists, update the existing one
            existing = SiteSettings.objects.first()
            self.pk = existing.pk
        super().save(*args, **kwargs)
    
    @classmethod
    def get_settings(cls):
        """Get the site settings instance, create if doesn't exist."""
        settings, created = cls.objects.get_or_create(pk=1)
        return settings


class ShippingZone(models.Model):
    """
    Shipping zones with different rates.
    """
    name = models.CharField(max_length=100, help_text="Zone name (e.g., Karachi, Lahore)")
    code = models.CharField(max_length=20, unique=True, help_text="Zone code (e.g., KHI, LHE)")
    
    # Shipping costs for this zone
    standard_cost = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=Decimal('500.00'),
        validators=[MinValueValidator(Decimal('0'))],
        help_text="Standard shipping cost for this zone (PKR)"
    )
    express_cost = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=Decimal('1000.00'),
        validators=[MinValueValidator(Decimal('0'))],
        help_text="Express shipping cost for this zone (PKR)"
    )
    
    # Delivery time estimates
    standard_delivery_days = models.PositiveIntegerField(
        default=3,
        help_text="Standard delivery time in days"
    )
    express_delivery_days = models.PositiveIntegerField(
        default=1,
        help_text="Express delivery time in days"
    )
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Shipping Zone"
        verbose_name_plural = "Shipping Zones"
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.code})"


class TaxRate(models.Model):
    """
    Tax rates for different regions/categories.
    """
    name = models.CharField(max_length=100, help_text="Tax rate name (e.g., GST, VAT)")
    rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0')), MaxValueValidator(Decimal('100'))],
        help_text="Tax rate as percentage"
    )
    
    # Optional: Apply to specific regions or product categories
    region = models.CharField(max_length=100, blank=True, help_text="Region (optional)")
    category = models.ForeignKey(
        'products.Category',
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        help_text="Product category (optional)"
    )
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Tax Rate"
        verbose_name_plural = "Tax Rates"
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.rate}%)"
