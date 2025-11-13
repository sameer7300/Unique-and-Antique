"""
URL patterns for the products app.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers
from . import views, admin_views

app_name = 'products'

# Main router
router = DefaultRouter()
router.register(r'categories', views.CategoryViewSet, basename='category')
router.register(r'brands', views.BrandViewSet, basename='brand')
router.register(r'products', views.ProductViewSet, basename='product')

# Nested routers for product images and variants
products_router = routers.NestedDefaultRouter(router, r'products', lookup='product')
products_router.register(r'images', views.ProductImageViewSet, basename='product-images')
products_router.register(r'variants', views.ProductVariantViewSet, basename='product-variants')

urlpatterns = [
    # Main API endpoints
    path('', include(router.urls)),
    path('', include(products_router.urls)),
    
    # Additional endpoints
    path('categories/tree/', views.get_categories_tree, name='categories-tree'),
    path('featured/', views.get_featured_products, name='featured-products'),
    path('shuffled/', views.get_shuffled_products, name='shuffled-products'),
    path('products/<int:pk>/recommendations/', 
         views.ProductRecommendationView.as_view(), 
         name='product-recommendations'),
    path('compare/', views.ProductComparisonView.as_view(), name='product-comparison'),
    
    # Admin endpoints
    path('admin/products/stats/', admin_views.AdminProductStatsView.as_view(), name='admin_product_stats'),
    path('admin/products/', admin_views.AdminProductListView.as_view(), name='admin_product_list'),
    path('admin/products/<int:pk>/', admin_views.AdminProductDetailView.as_view(), name='admin_product_detail'),
]
