"""
URL patterns for the accounts app.
"""

from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views, admin_views

app_name = 'accounts'

urlpatterns = [
    # Authentication
    path('register/', views.UserRegistrationView.as_view(), name='register'),
    path('login/', views.UserLoginView.as_view(), name='login'),
    path('login/2fa/', views.UserLogin2FAView.as_view(), name='login_2fa'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # User Profile
    path('profile/', views.UserProfileView.as_view(), name='profile'),
    path('dashboard/', views.user_dashboard, name='dashboard'),
    
    # Password Management
    path('change-password/', views.ChangePasswordView.as_view(), name='change_password'),
    path('password-reset/request/', views.request_password_reset, name='password_reset_request'),
    path('password-reset/verify/', views.verify_reset_code, name='password_reset_verify'),
    path('password-reset/confirm/', views.reset_password_confirm, name='password_reset_confirm_new'),
    
    # Email Verification
    path('email-verification/verify/', views.verify_email, name='verify_email'),
    path('email-verification/resend/', views.resend_verification_code, name='resend_verification'),
    
    # Addresses
    path('addresses/', views.AddressListCreateView.as_view(), name='address_list'),
    path('addresses/<int:pk>/', views.AddressDetailView.as_view(), name='address_detail'),
    
    # Two-Factor Authentication
    path('2fa/setup/', views.TwoFactorSetupView.as_view(), name='2fa_setup'),
    path('2fa/verify/', views.TwoFactorVerifyView.as_view(), name='2fa_verify'),
    path('2fa/disable/', views.TwoFactorDisableView.as_view(), name='2fa_disable'),
    path('2fa/status/', views.TwoFactorStatusView.as_view(), name='2fa_status'),
    
    # Account Management
    path('delete-account/', views.DeleteAccountView.as_view(), name='delete_account'),
    
    # Admin endpoints
    path('admin/users/stats/', admin_views.AdminUserStatsView.as_view(), name='admin_user_stats'),
    path('admin/users/', admin_views.AdminUserListView.as_view(), name='admin_user_list'),
    path('admin/users/<int:pk>/', admin_views.AdminUserDetailView.as_view(), name='admin_user_detail'),
    path('admin/activity/recent/', admin_views.admin_activity_recent, name='admin_activity_recent'),
]
