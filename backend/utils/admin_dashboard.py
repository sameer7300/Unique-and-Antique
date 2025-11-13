"""
Custom admin dashboard configuration for enhanced e-commerce management.
"""

from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.urls import path
from django.shortcuts import render
from django.db.models import Count, Sum, Avg
from django.utils import timezone
from datetime import timedelta

from apps.accounts.models import User
from apps.products.models import Product, Category, Brand
from apps.orders.models import Order
from apps.payments.models import Payment
from apps.reviews.models import Review
from apps.cart.models import Cart
from apps.settings.models import SiteSettings, ShippingZone, TaxRate


class EcommerceAdminSite(admin.AdminSite):
    """
    Custom admin site with enhanced dashboard.
    """
    site_header = _('Unique and Antique E-commerce Admin')
    site_title = _('E-commerce Admin')
    index_title = _('E-commerce Dashboard')
    
    def get_urls(self):
        """Add custom dashboard URLs."""
        urls = super().get_urls()
        custom_urls = [
            path('dashboard/', self.admin_view(self.dashboard_view), name='dashboard'),
            path('analytics/', self.admin_view(self.analytics_view), name='analytics'),
        ]
        return custom_urls + urls
    
    def dashboard_view(self, request):
        """Custom dashboard view with key metrics."""
        # Get date ranges
        today = timezone.now().date()
        week_ago = today - timedelta(days=7)
        month_ago = today - timedelta(days=30)
        
        # User statistics
        total_users = User.objects.count()
        new_users_week = User.objects.filter(created_at__gte=week_ago).count()
        active_users = User.objects.filter(is_active=True).count()
        
        # Product statistics
        total_products = Product.objects.count()
        active_products = Product.objects.filter(status='active').count()
        low_stock_products = Product.objects.filter(
            track_inventory=True,
            stock__lte=10
        ).count()
        out_of_stock = Product.objects.filter(
            track_inventory=True,
            stock=0
        ).count()
        
        # Order statistics
        total_orders = Order.objects.count()
        orders_week = Order.objects.filter(created_at__gte=week_ago).count()
        pending_orders = Order.objects.filter(status='pending').count()
        revenue_month = Order.objects.filter(
            created_at__gte=month_ago,
            payment_status='paid'
        ).aggregate(total=Sum('total_amount'))['total'] or 0
        
        # Payment statistics
        successful_payments = Payment.objects.filter(status='succeeded').count()
        failed_payments = Payment.objects.filter(status='failed').count()
        
        # Review statistics
        total_reviews = Review.objects.count()
        pending_reviews = Review.objects.filter(status='pending').count()
        avg_rating = Review.objects.filter(status='approved').aggregate(
            avg=Avg('rating')
        )['avg'] or 0
        
        # Cart statistics
        active_carts = Cart.objects.filter(status='active').count()
        abandoned_carts = Cart.objects.filter(status='abandoned').count()
        
        # Site settings
        site_settings = SiteSettings.get_settings()
        shipping_zones_count = ShippingZone.objects.filter(is_active=True).count()
        tax_rates_count = TaxRate.objects.filter(is_active=True).count()
        
        # Recent activity
        recent_orders = Order.objects.select_related('user').order_by('-created_at')[:5]
        recent_reviews = Review.objects.select_related('user', 'product').order_by('-created_at')[:5]
        recent_users = User.objects.order_by('-created_at')[:5]
        
        context = {
            'title': _('Dashboard'),
            'user_stats': {
                'total': total_users,
                'new_week': new_users_week,
                'active': active_users,
            },
            'product_stats': {
                'total': total_products,
                'active': active_products,
                'low_stock': low_stock_products,
                'out_of_stock': out_of_stock,
            },
            'order_stats': {
                'total': total_orders,
                'week': orders_week,
                'pending': pending_orders,
                'revenue_month': revenue_month,
            },
            'payment_stats': {
                'successful': successful_payments,
                'failed': failed_payments,
            },
            'review_stats': {
                'total': total_reviews,
                'pending': pending_reviews,
                'avg_rating': round(avg_rating, 2),
            },
            'cart_stats': {
                'active': active_carts,
                'abandoned': abandoned_carts,
            },
            'settings_stats': {
                'site_settings': site_settings,
                'shipping_zones': shipping_zones_count,
                'tax_rates': tax_rates_count,
                'currency': site_settings.currency_code,
                'tax_enabled': site_settings.tax_enabled,
                'shipping_enabled': site_settings.shipping_enabled,
            },
            'recent_orders': recent_orders,
            'recent_reviews': recent_reviews,
            'recent_users': recent_users,
        }
        
        return render(request, 'admin/dashboard.html', context)
    
    def analytics_view(self, request):
        """Analytics view with charts and detailed metrics."""
        # Get date ranges
        today = timezone.now().date()
        days_30 = today - timedelta(days=30)
        
        # Sales analytics
        daily_sales = []
        for i in range(30):
            date = today - timedelta(days=i)
            sales = Order.objects.filter(
                created_at__date=date,
                payment_status='paid'
            ).aggregate(total=Sum('total_amount'))['total'] or 0
            daily_sales.append({
                'date': date.strftime('%Y-%m-%d'),
                'sales': float(sales)
            })
        
        # Product performance
        top_products = Product.objects.annotate(
            order_count=Count('order_items')
        ).order_by('-order_count')[:10]
        
        # Category performance
        category_sales = Category.objects.annotate(
            sales=Sum('products__order_items__total_price')
        ).order_by('-sales')[:10]
        
        # User registration trends
        user_registrations = []
        for i in range(30):
            date = today - timedelta(days=i)
            count = User.objects.filter(created_at__date=date).count()
            user_registrations.append({
                'date': date.strftime('%Y-%m-%d'),
                'count': count
            })
        
        context = {
            'title': _('Analytics'),
            'daily_sales': daily_sales,
            'top_products': top_products,
            'category_sales': category_sales,
            'user_registrations': user_registrations,
        }
        
        return render(request, 'admin/analytics.html', context)


# Create custom admin site instance
ecommerce_admin = EcommerceAdminSite(name='ecommerce_admin')


def get_admin_stats():
    """
    Get comprehensive admin statistics for dashboard widgets.
    """
    today = timezone.now().date()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)
    
    stats = {
        'users': {
            'total': User.objects.count(),
            'active': User.objects.filter(is_active=True).count(),
            'new_this_week': User.objects.filter(created_at__gte=week_ago).count(),
            'customers': User.objects.filter(role='customer').count(),
            'staff': User.objects.filter(role__in=['staff', 'admin']).count(),
        },
        'products': {
            'total': Product.objects.count(),
            'active': Product.objects.filter(status='active').count(),
            'featured': Product.objects.filter(is_featured=True).count(),
            'low_stock': Product.objects.filter(
                track_inventory=True,
                stock__lte=10
            ).count(),
            'out_of_stock': Product.objects.filter(
                track_inventory=True,
                stock=0
            ).count(),
        },
        'orders': {
            'total': Order.objects.count(),
            'pending': Order.objects.filter(status='pending').count(),
            'processing': Order.objects.filter(status='processing').count(),
            'shipped': Order.objects.filter(status='shipped').count(),
            'delivered': Order.objects.filter(status='delivered').count(),
            'this_week': Order.objects.filter(created_at__gte=week_ago).count(),
            'revenue_month': Order.objects.filter(
                created_at__gte=month_ago,
                payment_status='paid'
            ).aggregate(total=Sum('total_amount'))['total'] or 0,
        },
        'payments': {
            'total': Payment.objects.count(),
            'successful': Payment.objects.filter(status='succeeded').count(),
            'failed': Payment.objects.filter(status='failed').count(),
            'pending': Payment.objects.filter(status='pending').count(),
            'refunded': Payment.objects.filter(status='refunded').count(),
        },
        'reviews': {
            'total': Review.objects.count(),
            'pending': Review.objects.filter(status='pending').count(),
            'approved': Review.objects.filter(status='approved').count(),
            'flagged': Review.objects.filter(status='flagged').count(),
            'avg_rating': Review.objects.filter(status='approved').aggregate(
                avg=Avg('rating')
            )['avg'] or 0,
        },
        'categories': Category.objects.filter(is_active=True).count(),
        'brands': Brand.objects.filter(is_active=True).count(),
        'settings': {
            'site_settings': SiteSettings.get_settings(),
            'shipping_zones': ShippingZone.objects.filter(is_active=True).count(),
            'tax_rates': TaxRate.objects.filter(is_active=True).count(),
        },
    }
    
    return stats


class AdminDashboardMixin:
    """
    Mixin to add dashboard functionality to admin classes.
    """
    
    def changelist_view(self, request, extra_context=None):
        """Add dashboard stats to changelist context."""
        extra_context = extra_context or {}
        extra_context['admin_stats'] = get_admin_stats()
        return super().changelist_view(request, extra_context)


# Admin action helpers
def export_to_csv(modeladmin, request, queryset):
    """Export selected items to CSV."""
    import csv
    from django.http import HttpResponse
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{modeladmin.model._meta.verbose_name_plural}.csv"'
    
    writer = csv.writer(response)
    
    # Write headers
    field_names = [field.name for field in modeladmin.model._meta.fields]
    writer.writerow(field_names)
    
    # Write data
    for obj in queryset:
        row = []
        for field in field_names:
            value = getattr(obj, field)
            if callable(value):
                value = value()
            row.append(str(value))
        writer.writerow(row)
    
    return response

export_to_csv.short_description = _('Export selected items to CSV')


def send_notification_email(modeladmin, request, queryset):
    """Send notification email for selected items."""
    from django.core.mail import send_mail
    from django.conf import settings
    
    count = queryset.count()
    subject = f'Admin Notification: {count} {modeladmin.model._meta.verbose_name_plural}'
    message = f'This is a notification about {count} selected {modeladmin.model._meta.verbose_name_plural}.'
    
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[request.user.email],
            fail_silently=False,
        )
        modeladmin.message_user(request, f'Notification email sent for {count} items.')
    except Exception as e:
        modeladmin.message_user(
            request, 
            f'Error sending email: {str(e)}',
            level='ERROR'
        )

send_notification_email.short_description = _('Send notification email')
