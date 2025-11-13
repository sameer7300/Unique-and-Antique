"""
URL patterns for the orders app.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views, admin_views

app_name = 'orders'

# Router for viewsets
router = DefaultRouter()
router.register(r'orders', views.OrderViewSet, basename='order')
router.register(r'returns', views.OrderReturnViewSet, basename='orderreturn')

urlpatterns = [
    # ViewSet URLs
    path('', include(router.urls)),
    
    # Admin endpoints
    path('admin/orders/stats/', admin_views.AdminOrderStatsView.as_view(), name='admin_order_stats'),
    path('admin/orders/', admin_views.AdminOrderListView.as_view(), name='admin_order_list'),
    path('admin/orders/<int:pk>/', admin_views.AdminOrderDetailView.as_view(), name='admin_order_detail'),
]
