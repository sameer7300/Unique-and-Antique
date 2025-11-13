"""
Custom admin dashboard for non-IT administrators
"""

from django.contrib import admin
from django.template.response import TemplateResponse
from django.urls import path
from django.utils.html import format_html
from django.db.models import Count, Sum, Avg, Q
from django.utils import timezone
from datetime import datetime, timedelta
from apps.products.models import Product, Category, Brand
from apps.orders.models import Order
from apps.accounts.models import User


class CustomAdminSite(admin.AdminSite):
    """Custom admin site with user-friendly dashboard"""
    
    site_header = "🏪 Unique & Antique - Store Management"
    site_title = "Store Admin"
    index_title = "Welcome to your Store Dashboard!"
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('dashboard/', self.admin_view(self.dashboard_view), name='dashboard'),
            path('quick-help/', self.admin_view(self.help_view), name='quick_help'),
        ]
        return custom_urls + urls
    
    def _get_pending_reviews(self):
        """Get pending reviews that need admin approval"""
        try:
            from apps.reviews.models import Review
            return Review.objects.filter(
                status='pending'
            ).select_related('user', 'product').order_by('-created_at')
        except ImportError:
            return []

    def _get_review_stats(self, today, week_ago, month_ago):
        """Get comprehensive review statistics"""
        try:
            from apps.reviews.models import Review
            return {
                'total_reviews': Review.objects.count(),
                'pending_reviews': Review.objects.filter(status='pending').count(),
                'approved_reviews': Review.objects.filter(status='approved').count(),
                'rejected_reviews': Review.objects.filter(status='rejected').count(),
                'reviews_today': Review.objects.filter(created_at__date=today).count(),
                'reviews_this_week': Review.objects.filter(created_at__date__gte=week_ago).count(),
                'reviews_this_month': Review.objects.filter(created_at__date__gte=month_ago).count(),
                'avg_rating': Review.objects.filter(status='approved').aggregate(
                    avg_rating=Avg('rating'))['avg_rating'] or 0,
            }
        except ImportError:
            return {
                'total_reviews': 0,
                'pending_reviews': 0,
                'approved_reviews': 0,
                'rejected_reviews': 0,
                'reviews_today': 0,
                'reviews_this_week': 0,
                'reviews_this_month': 0,
                'avg_rating': 0,
            }

    def dashboard_view(self, request):
        """Custom dashboard view with business metrics"""
        
        # 📊 CALCULATE METRICS
        # Get date ranges for calculations
        today = timezone.now().date()
        yesterday = today - timedelta(days=1)
        week_ago = today - timedelta(days=7)
        month_ago = today - timedelta(days=30)
        year_ago = today - timedelta(days=365)
        
        # Calculate comprehensive metrics
        context = {
            'title': 'Store Dashboard',
            'site_title': self.site_title,
            'site_header': self.site_header,
            
            # 📦 PRODUCT METRICS
            'product_stats': {
                'total_products': Product.objects.count(),
                'active_products': Product.objects.filter(status='active').count(),
                'draft_products': Product.objects.filter(status='draft').count(),
                'featured_products': Product.objects.filter(is_featured=True).count(),
                'low_stock_count': Product.objects.filter(stock__lte=10, track_inventory=True).count(),
                'out_of_stock_count': Product.objects.filter(stock=0, track_inventory=True).count(),
                'avg_product_price': Product.objects.filter(status='active').aggregate(
                    avg_price=Avg('price'))['avg_price'] or 0,
            },
            
            # 🏷️ CATEGORY METRICS
            'category_stats': {
                'total_categories': Category.objects.count(),
                'active_categories': Category.objects.filter(is_active=True).count(),
                'inactive_categories': Category.objects.filter(is_active=False).count(),
                'parent_categories': Category.objects.filter(parent__isnull=True).count(),
                'child_categories': Category.objects.filter(parent__isnull=False).count(),
                'categories_with_products': Category.objects.annotate(
                    product_count=Count('products', filter=Q(products__status='active'))
                ).filter(product_count__gt=0).count(),
                'empty_categories': Category.objects.annotate(
                    product_count=Count('products', filter=Q(products__status='active'))
                ).filter(product_count=0).count(),
            },
            
            # 🛒 ORDER METRICS
            'order_stats': {
                'total_orders': Order.objects.count(),
                'orders_today': Order.objects.filter(created_at__date=today).count(),
                'orders_yesterday': Order.objects.filter(created_at__date=yesterday).count(),
                'orders_this_week': Order.objects.filter(created_at__date__gte=week_ago).count(),
                'orders_this_month': Order.objects.filter(created_at__date__gte=month_ago).count(),
                'pending_orders': Order.objects.filter(status='pending').count(),
                'processing_orders': Order.objects.filter(status='processing').count(),
                'confirmed_orders': Order.objects.filter(status='confirmed').count(),
                'delivered_orders': Order.objects.filter(status='delivered').count(),
                'cancelled_orders': Order.objects.filter(status='cancelled').count(),
            },
            
            # 💰 REVENUE METRICS
            'revenue_stats': {
                'total_revenue': Order.objects.filter(
                    payment_status='paid'
                ).aggregate(total=Sum('total_amount'))['total'] or 0,
                'revenue_today': Order.objects.filter(
                    created_at__date=today, 
                    payment_status='paid'
                ).aggregate(total=Sum('total_amount'))['total'] or 0,
                'revenue_yesterday': Order.objects.filter(
                    created_at__date=yesterday, 
                    payment_status='paid'
                ).aggregate(total=Sum('total_amount'))['total'] or 0,
                'revenue_this_week': Order.objects.filter(
                    created_at__date__gte=week_ago, 
                    payment_status='paid'
                ).aggregate(total=Sum('total_amount'))['total'] or 0,
                'revenue_this_month': Order.objects.filter(
                    created_at__date__gte=month_ago, 
                    payment_status='paid'
                ).aggregate(total=Sum('total_amount'))['total'] or 0,
                'revenue_this_year': Order.objects.filter(
                    created_at__date__gte=year_ago, 
                    payment_status='paid'
                ).aggregate(total=Sum('total_amount'))['total'] or 0,
                'avg_order_value': Order.objects.filter(
                    payment_status='paid'
                ).aggregate(avg_value=Avg('total_amount'))['avg_value'] or 0,
            },
            
            # 👥 CUSTOMER METRICS
            'customer_stats': {
                'total_customers': User.objects.filter(is_staff=False).count(),
                'new_customers_today': User.objects.filter(
                    date_joined__date=today, is_staff=False
                ).count(),
                'new_customers_this_week': User.objects.filter(
                    date_joined__date__gte=week_ago, is_staff=False
                ).count(),
                'new_customers_this_month': User.objects.filter(
                    date_joined__date__gte=month_ago, is_staff=False
                ).count(),
                'active_customers': User.objects.filter(
                    is_staff=False, orders__created_at__gte=month_ago
                ).distinct().count(),
            },

            # ⭐ REVIEW METRICS
            'review_stats': self._get_review_stats(today, week_ago, month_ago),
            
            # 🚨 ALERTS & WARNINGS
            'alerts': {
                'low_stock_items': Product.objects.filter(
                    stock__lte=10, stock__gt=0, track_inventory=True
                ).order_by('stock')[:10],
                'out_of_stock_items': Product.objects.filter(
                    stock=0, track_inventory=True
                ).order_by('title')[:10],
                'empty_categories': Category.objects.annotate(
                    product_count=Count('products', filter=Q(products__status='active'))
                ).filter(product_count=0, is_active=True).order_by('name')[:5],
                'pending_orders': Order.objects.filter(
                    status='pending'
                ).order_by('-created_at')[:5],
                'pending_reviews': self._get_pending_reviews()[:8],
                'recent_orders': Order.objects.select_related('user').order_by('-created_at')[:8],
            },
            
            # 📊 TOP PERFORMERS
            'top_performers': {
                'best_selling_products': Product.objects.filter(
                    status='active'
                ).annotate(
                    order_count=Count('order_items__order', distinct=True)
                ).order_by('-order_count')[:5],
                'highest_revenue_products': Product.objects.filter(
                    status='active'
                ).annotate(
                    total_revenue=Sum('order_items__total_price')
                ).order_by('-total_revenue')[:5],
                'most_popular_categories': Category.objects.filter(
                    is_active=True
                ).annotate(
                    product_count=Count('products', filter=Q(products__status='active')),
                    order_count=Count('products__order_items__order', distinct=True)
                ).filter(product_count__gt=0).order_by('-order_count')[:5],
                'top_customers': User.objects.filter(
                    is_staff=False
                ).annotate(
                    total_spent=Sum('orders__total_amount', filter=Q(orders__status='completed'))
                ).order_by('-total_spent')[:5],
            },
            
            # Quick actions
            'quick_actions': [
                {
                    'title': '➕ Add New Product',
                    'url': '/admin/products/product/add/',
                    'description': 'Add a new product to your store',
                    'icon': '📦'
                },
                {
                    'title': '🏷️ Manage Categories',
                    'url': '/admin/products/category/',
                    'description': 'Organize products with categories',
                    'icon': '🏷️'
                },
                {
                    'title': '➕ Add New Category',
                    'url': '/admin/products/category/add/',
                    'description': 'Create a new product category',
                    'icon': '🆕'
                },
                {
                    'title': '📋 View Orders',
                    'url': '/admin/orders/order/',
                    'description': 'Check and manage customer orders',
                    'icon': '🛒'
                },
                {
                    'title': '⭐ Manage Reviews',
                    'url': '/admin/reviews/review/',
                    'description': 'Approve or reject customer reviews',
                    'icon': '⭐'
                },
                {
                    'title': '👥 View Customers',
                    'url': '/admin/accounts/user/',
                    'description': 'Manage customer accounts',
                    'icon': '👤'
                },
                {
                    'title': '📊 Export Data',
                    'url': '/admin/products/product/',
                    'description': 'Export products to Excel/CSV',
                    'icon': '📈'
                }
            ],
            
            # Help tips
            'help_tips': [
                {
                    'title': '💡 Managing Products',
                    'content': 'Always set clear titles and descriptions. Use high-quality images and set appropriate stock levels.',
                },
                {
                    'title': '🏷️ Organizing Categories',
                    'content': 'Create logical category structures. Use parent categories for main groups and child categories for specific types. Keep category names clear and customer-friendly.',
                },
                {
                    'title': '🔄 Processing Orders',
                    'content': 'Check orders daily. Update order status to keep customers informed about their purchases.',
                },
                {
                    'title': '📈 Growing Sales',
                    'content': 'Feature your best products, offer competitive prices, and respond quickly to customer inquiries.',
                }
            ]
        }
        
        # Create response with cache-busting headers
        response = TemplateResponse(request, 'admin/custom_dashboard.html', context)
        response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response['Pragma'] = 'no-cache'
        response['Expires'] = '0'
        return response
    
    def help_view(self, request):
        """Quick help guide for administrators"""
        context = {
            'title': 'Quick Help Guide',
            'site_title': self.site_title,
            'site_header': self.site_header,
            'help_sections': [
                {
                    'title': '🚀 Getting Started',
                    'items': [
                        'Add your first product by clicking "Add Product" in the top menu',
                        'Upload high-quality product images',
                        'Set competitive prices and stock levels',
                        'Make sure to activate products so customers can see them'
                    ]
                },
                {
                    'title': '📦 Managing Products',
                    'items': [
                        'Use clear, descriptive titles that customers will search for',
                        'Write detailed descriptions highlighting key features',
                        'Choose the right category to help customers find products',
                        'Set low stock alerts to avoid running out of popular items'
                    ]
                },
                {
                    'title': '🏷️ Managing Categories',
                    'items': [
                        'Create main parent categories for broad product groups',
                        'Use child categories to organize specific product types',
                        'Keep category names simple and customer-friendly',
                        'Add category images to make browsing more visual',
                        'Set sort order to control how categories appear on your site',
                        'Regularly review and clean up empty categories'
                    ]
                },
                {
                    'title': '🛒 Processing Orders',
                    'items': [
                        'Check for new orders daily in the Orders section',
                        'Update order status as you process them',
                        'Send tracking information to customers when available',
                        'Respond to customer messages promptly'
                    ]
                },
                {
                    'title': '📊 Understanding Reports',
                    'items': [
                        'Use the Export button to download sales data',
                        'Check the dashboard for quick business overview',
                        'Monitor low stock alerts to reorder inventory',
                        'Track customer growth and popular products'
                    ]
                }
            ]
        }
        return TemplateResponse(request, 'admin/help_guide.html', context)
    
    def index(self, request, extra_context=None):
        """Override default admin index to show custom dashboard"""
        return self.dashboard_view(request)


# Create custom admin site instance
admin_site = CustomAdminSite(name='custom_admin')

# Register all models with the custom admin site
try:
    # Register Products models
    from apps.products.admin import ProductAdmin, CategoryAdmin, BrandAdmin
    from apps.products.models import Category, Brand, ProductImage, ProductVariant
    
    admin_site.register(Product, ProductAdmin)
    admin_site.register(Category, CategoryAdmin)
    admin_site.register(Brand, BrandAdmin)
    
    # Register product images and variants if admin classes exist
    try:
        from apps.products.admin import ProductImageAdmin, ProductVariantAdmin
        admin_site.register(ProductImage, ProductImageAdmin)
        admin_site.register(ProductVariant, ProductVariantAdmin)
    except ImportError:
        # Register with basic admin if custom admin doesn't exist
        admin_site.register(ProductImage)
        admin_site.register(ProductVariant)

    # Register Orders models
    from apps.orders.admin import OrderAdmin, OrderItemAdmin
    from apps.orders.models import OrderItem
    admin_site.register(Order, OrderAdmin)
    admin_site.register(OrderItem, OrderItemAdmin)

    # Register Accounts models
    try:
        from apps.accounts.admin import UserAdmin
        admin_site.register(User, UserAdmin)
    except ImportError:
        from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
        admin_site.register(User, BaseUserAdmin)

    # Register other models with basic admin if custom admin doesn't exist
    try:
        from apps.reviews.models import Review
        from apps.reviews.admin import ReviewAdmin
        admin_site.register(Review, ReviewAdmin)
    except ImportError:
        pass

    try:
        from apps.contact.models import ContactMessage
        admin_site.register(ContactMessage)
    except ImportError:
        pass

    try:
        from apps.newsletter.models import NewsletterSubscription
        admin_site.register(NewsletterSubscription)
    except ImportError:
        pass

    try:
        from apps.settings.models import SiteSettings
        admin_site.register(SiteSettings)
    except ImportError:
        pass

except ImportError as e:
    print(f"Warning: Could not register some admin models: {e}")
