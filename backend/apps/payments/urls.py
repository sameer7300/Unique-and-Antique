"""
URL patterns for the payments app.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'payments'

# Router for viewsets
router = DefaultRouter()
router.register(r'payments', views.PaymentViewSet, basename='payment')
router.register(r'methods', views.PaymentMethodViewSet, basename='paymentmethod')

urlpatterns = [
    # ViewSet URLs
    path('', include(router.urls)),
    
    # Payment processing endpoints
    path('intents/', views.PaymentIntentView.as_view(), name='payment-intent'),
    path('cod/', views.CODPaymentView.as_view(), name='cod-payment'),
    
    # Webhook endpoints
    path('webhooks/stripe/', views.PaymentWebhookView.as_view(), name='stripe-webhook'),
    
    # Report endpoints
    path('reports/', views.PaymentReportView.as_view(), name='payment-reports'),
]
