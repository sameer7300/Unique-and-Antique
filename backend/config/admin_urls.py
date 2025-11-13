"""
Admin API URLs for the Unique and Antique E-commerce Platform.
Aggregates admin endpoints from all apps.
"""

from django.urls import path, include

# Import admin views from each app
from apps.accounts.admin_views import (
    AdminUserStatsView, 
    AdminUserListView, 
    AdminUserDetailView, 
    admin_activity_recent
)
from apps.products.admin_views import (
    AdminProductStatsView,
    AdminProductListView,
    AdminProductDetailView
)
from apps.orders.admin_views import (
    AdminOrderStatsView,
    AdminOrderListView,
    AdminOrderDetailView
)
from apps.reviews.admin_views import (
    AdminReviewStatsView,
    AdminReviewListView,
    AdminReviewDetailView
)
from apps.contact.admin_views import (
    AdminContactStatsView,
    AdminContactListView,
    AdminContactDetailView
)

urlpatterns = [
    # User management
    path('users/stats/', AdminUserStatsView.as_view(), name='admin_user_stats'),
    path('users/', AdminUserListView.as_view(), name='admin_user_list'),
    path('users/<int:pk>/', AdminUserDetailView.as_view(), name='admin_user_detail'),
    
    # Activity
    path('activity/recent/', admin_activity_recent, name='admin_activity_recent'),
    
    # Product management
    path('products/stats/', AdminProductStatsView.as_view(), name='admin_product_stats'),
    path('products/', AdminProductListView.as_view(), name='admin_product_list'),
    path('products/<int:pk>/', AdminProductDetailView.as_view(), name='admin_product_detail'),
    
    # Order management
    path('orders/stats/', AdminOrderStatsView.as_view(), name='admin_order_stats'),
    path('orders/', AdminOrderListView.as_view(), name='admin_order_list'),
    path('orders/<int:pk>/', AdminOrderDetailView.as_view(), name='admin_order_detail'),
    
    # Review management
    path('reviews/stats/', AdminReviewStatsView.as_view(), name='admin_review_stats'),
    path('reviews/', AdminReviewListView.as_view(), name='admin_review_list'),
    path('reviews/<int:pk>/', AdminReviewDetailView.as_view(), name='admin_review_detail'),
    
    # Contact management
    path('contact/stats/', AdminContactStatsView.as_view(), name='admin_contact_stats'),
    path('contact/', AdminContactListView.as_view(), name='admin_contact_list'),
    path('contact/<int:pk>/', AdminContactDetailView.as_view(), name='admin_contact_detail'),
]
