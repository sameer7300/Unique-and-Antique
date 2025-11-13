"""
URL patterns for the settings app.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'settings'

# Router for viewsets
router = DefaultRouter()
router.register(r'shipping-zones', views.ShippingZoneViewSet, basename='shippingzone')
router.register(r'tax-rates', views.TaxRateViewSet, basename='taxrate')

urlpatterns = [
    # ViewSet URLs
    path('', include(router.urls)),
    
    # Site settings endpoint
    path('site/', views.SiteSettingsView.as_view(), name='site-settings'),
]
