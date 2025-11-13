"""
URL patterns for the cart app.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'cart'

# Router for viewsets
router = DefaultRouter()
router.register(r'carts', views.CartViewSet, basename='cart')
router.register(r'items', views.CartItemViewSet, basename='cartitem')
router.register(r'saved', views.SavedItemViewSet, basename='saveditem')

urlpatterns = [
    # ViewSet URLs
    path('', include(router.urls)),
    
    # Guest cart endpoints
    path('guest/', views.GuestCartView.as_view(), name='guest-cart'),
    
    # Cart management endpoints
    path('merge/', views.MergeCartsView.as_view(), name='merge-carts'),
    path('stats/', views.CartStatsView.as_view(), name='cart-stats'),
]
