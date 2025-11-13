"""
Admin configuration for settings app.
"""

from django.contrib import admin
from .models import SiteSettings, ShippingZone, TaxRate


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    """
    Admin interface for site settings.
    """
    list_display = [
        'tax_rate', 'tax_enabled', 'free_shipping_threshold', 
        'standard_shipping_cost', 'currency_code', 'updated_at'
    ]
    
    fieldsets = (
        ('Tax Settings', {
            'fields': ('tax_rate', 'tax_enabled'),
            'description': 'Configure tax calculation settings'
        }),
        ('Shipping Settings', {
            'fields': (
                'free_shipping_threshold', 'standard_shipping_cost', 
                'express_shipping_cost', 'shipping_enabled'
            ),
            'description': 'Configure shipping cost settings'
        }),
        ('Currency Settings', {
            'fields': ('currency_code', 'currency_symbol'),
            'description': 'Configure currency display settings'
        }),
        ('Order Settings', {
            'fields': ('minimum_order_amount',),
            'description': 'Configure order-related settings'
        }),
    )
    
    def has_add_permission(self, request):
        """Only allow one instance of site settings."""
        return not SiteSettings.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        """Don't allow deletion of site settings."""
        return False


@admin.register(ShippingZone)
class ShippingZoneAdmin(admin.ModelAdmin):
    """
    Admin interface for shipping zones.
    """
    list_display = [
        'name', 'code', 'standard_cost', 'express_cost', 
        'standard_delivery_days', 'express_delivery_days', 'is_active'
    ]
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'code']
    list_editable = ['is_active']
    
    fieldsets = (
        ('Zone Information', {
            'fields': ('name', 'code', 'is_active')
        }),
        ('Shipping Costs', {
            'fields': ('standard_cost', 'express_cost')
        }),
        ('Delivery Times', {
            'fields': ('standard_delivery_days', 'express_delivery_days')
        }),
    )


@admin.register(TaxRate)
class TaxRateAdmin(admin.ModelAdmin):
    """
    Admin interface for tax rates.
    """
    list_display = ['name', 'rate', 'region', 'category', 'is_active']
    list_filter = ['is_active', 'category', 'created_at']
    search_fields = ['name', 'region']
    list_editable = ['is_active']
    
    fieldsets = (
        ('Tax Information', {
            'fields': ('name', 'rate', 'is_active')
        }),
        ('Application Scope', {
            'fields': ('region', 'category'),
            'description': 'Optional: Apply this tax rate to specific regions or product categories'
        }),
    )
