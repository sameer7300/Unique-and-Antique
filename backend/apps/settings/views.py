"""
Views for the settings app.
"""

from rest_framework import generics, viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import SiteSettings, ShippingZone, TaxRate
from .serializers import SiteSettingsSerializer, ShippingZoneSerializer, TaxRateSerializer


class SiteSettingsView(generics.RetrieveAPIView):
    """
    Get site settings (public endpoint for frontend).
    """
    serializer_class = SiteSettingsSerializer
    permission_classes = [permissions.AllowAny]
    
    def get_object(self):
        """Get the site settings instance."""
        return SiteSettings.get_settings()


class ShippingZoneViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for shipping zones (read-only for frontend).
    """
    serializer_class = ShippingZoneSerializer
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        """Get active shipping zones."""
        return ShippingZone.objects.filter(is_active=True)
    
    @action(detail=False, methods=['get'])
    def calculate_shipping(self, request):
        """
        Calculate shipping cost for a given zone and order amount.
        """
        zone_code = request.query_params.get('zone')
        order_amount = request.query_params.get('amount', 0)
        shipping_type = request.query_params.get('type', 'standard')  # standard or express
        
        try:
            order_amount = float(order_amount)
            settings = SiteSettings.get_settings()
            
            # Check for free shipping
            if order_amount >= float(settings.free_shipping_threshold):
                return Response({
                    'shipping_cost': 0,
                    'is_free': True,
                    'message': 'Free shipping applied'
                })
            
            # Get zone-specific shipping cost
            if zone_code:
                try:
                    zone = ShippingZone.objects.get(code=zone_code, is_active=True)
                    cost = zone.express_cost if shipping_type == 'express' else zone.standard_cost
                    delivery_days = zone.express_delivery_days if shipping_type == 'express' else zone.standard_delivery_days
                    
                    return Response({
                        'shipping_cost': cost,
                        'is_free': False,
                        'zone': zone.name,
                        'delivery_days': delivery_days,
                        'shipping_type': shipping_type
                    })
                except ShippingZone.DoesNotExist:
                    pass
            
            # Default shipping cost
            cost = settings.express_shipping_cost if shipping_type == 'express' else settings.standard_shipping_cost
            
            return Response({
                'shipping_cost': cost,
                'is_free': False,
                'shipping_type': shipping_type,
                'delivery_days': 1 if shipping_type == 'express' else 3
            })
            
        except (ValueError, TypeError):
            return Response({
                'error': 'Invalid order amount'
            }, status=400)


class TaxRateViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for tax rates (read-only for frontend).
    """
    serializer_class = TaxRateSerializer
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        """Get active tax rates."""
        return TaxRate.objects.filter(is_active=True)
    
    @action(detail=False, methods=['get'])
    def calculate_tax(self, request):
        """
        Calculate tax for a given amount and optional category/region.
        """
        amount = request.query_params.get('amount', 0)
        category_id = request.query_params.get('category')
        region = request.query_params.get('region')
        
        try:
            amount = float(amount)
            settings = SiteSettings.get_settings()
            
            if not settings.tax_enabled:
                return Response({
                    'tax_amount': 0,
                    'tax_rate': 0,
                    'message': 'Tax calculation disabled'
                })
            
            # Try to find specific tax rate
            tax_rate = None
            
            # First, try category-specific tax rate
            if category_id:
                tax_rate = TaxRate.objects.filter(
                    category_id=category_id,
                    is_active=True
                ).first()
            
            # Then, try region-specific tax rate
            if not tax_rate and region:
                tax_rate = TaxRate.objects.filter(
                    region=region,
                    is_active=True
                ).first()
            
            # Use the tax rate or fall back to site default
            rate = float(tax_rate.rate) if tax_rate else float(settings.tax_rate)
            tax_amount = (amount * rate) / 100
            
            return Response({
                'tax_amount': round(tax_amount, 2),
                'tax_rate': rate,
                'tax_name': tax_rate.name if tax_rate else 'Default Tax'
            })
            
        except (ValueError, TypeError):
            return Response({
                'error': 'Invalid amount'
            }, status=400)
