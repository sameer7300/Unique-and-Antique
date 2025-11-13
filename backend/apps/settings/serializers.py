"""
Serializers for the settings app.
"""

from rest_framework import serializers
from .models import SiteSettings, ShippingZone, TaxRate


class SiteSettingsSerializer(serializers.ModelSerializer):
    """
    Serializer for site settings.
    """
    
    class Meta:
        model = SiteSettings
        fields = [
            'tax_rate', 'tax_enabled', 'free_shipping_threshold',
            'standard_shipping_cost', 'express_shipping_cost', 'shipping_enabled',
            'currency_code', 'currency_symbol', 'minimum_order_amount'
        ]


class ShippingZoneSerializer(serializers.ModelSerializer):
    """
    Serializer for shipping zones.
    """
    
    class Meta:
        model = ShippingZone
        fields = [
            'id', 'name', 'code', 'standard_cost', 'express_cost',
            'standard_delivery_days', 'express_delivery_days', 'is_active'
        ]


class TaxRateSerializer(serializers.ModelSerializer):
    """
    Serializer for tax rates.
    """
    category_name = serializers.CharField(source='category.name', read_only=True)
    
    class Meta:
        model = TaxRate
        fields = [
            'id', 'name', 'rate', 'region', 'category', 'category_name', 'is_active'
        ]
