"""
URL patterns for the reviews app.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views, admin_views

app_name = 'reviews'

# Router for viewsets
router = DefaultRouter()
router.register(r'reviews', views.ReviewViewSet, basename='review')
router.register(r'responses', views.ReviewResponseViewSet, basename='reviewresponse')
router.register(r'reports', views.ReviewReportViewSet, basename='reviewreport')

urlpatterns = [
    # ViewSet URLs
    path('', include(router.urls)),
    
    # Product-specific review endpoints
    path('products/<int:product_id>/summary/', 
         views.ProductReviewSummaryView.as_view(), 
         name='product-review-summary'),
    path('products/<int:product_id>/rating/', 
         views.ProductRatingView.as_view(), 
         name='product-rating'),
    
    # Admin endpoints
    path('admin/reviews/stats/', admin_views.AdminReviewStatsView.as_view(), name='admin_review_stats'),
    path('admin/reviews/', admin_views.AdminReviewListView.as_view(), name='admin_review_list'),
    path('admin/reviews/<int:pk>/', admin_views.AdminReviewDetailView.as_view(), name='admin_review_detail'),
]
