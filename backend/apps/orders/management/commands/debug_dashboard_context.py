from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from django.db.models import Sum, Count, Avg
from apps.orders.models import Order
from apps.products.models import Product, Category
from apps.accounts.models import User


class Command(BaseCommand):
    help = 'Debug the exact context data sent to dashboard template'

    def handle(self, *args, **options):
        self.stdout.write("🔍 DEBUGGING DASHBOARD CONTEXT DATA")
        self.stdout.write("=" * 50)
        
        # Replicate the exact logic from dashboard admin view
        today = timezone.now().date()
        yesterday = today - timedelta(days=1)
        week_ago = today - timedelta(days=7)
        month_ago = today - timedelta(days=30)
        year_ago = today - timedelta(days=365)
        
        # 💰 REVENUE METRICS (exact same logic as admin.py)
        revenue_stats = {
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
            ).aggregate(avg=Avg('total_amount'))['avg'] or 0,
        }
        
        # 🛒 ORDER METRICS
        order_stats = {
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
        }
        
        # 📦 PRODUCT METRICS
        product_stats = {
            'total_products': Product.objects.count(),
            'active_products': Product.objects.filter(status='active').count(),
            'draft_products': Product.objects.filter(status='draft').count(),
            'inactive_products': Product.objects.filter(status='inactive').count(),
        }
        
        # 👥 USER METRICS
        user_stats = {
            'total_users': User.objects.count(),
            'active_users': User.objects.filter(is_active=True).count(),
            'verified_users': User.objects.filter(is_active=True).count(),
        }
        
        # 🏷️ CATEGORY METRICS
        category_stats = {
            'total_categories': Category.objects.count(),
        }
        
        self.stdout.write("💰 REVENUE STATS:")
        for key, value in revenue_stats.items():
            self.stdout.write(f"   {key}: {value}")
        
        self.stdout.write("\n🛒 ORDER STATS:")
        for key, value in order_stats.items():
            self.stdout.write(f"   {key}: {value}")
        
        self.stdout.write("\n📦 PRODUCT STATS:")
        for key, value in product_stats.items():
            self.stdout.write(f"   {key}: {value}")
        
        self.stdout.write("\n👥 USER STATS:")
        for key, value in user_stats.items():
            self.stdout.write(f"   {key}: {value}")
        
        self.stdout.write("\n🏷️ CATEGORY STATS:")
        for key, value in category_stats.items():
            self.stdout.write(f"   {key}: {value}")
        
        # Show what the template variables should be
        self.stdout.write("\n📊 TEMPLATE VARIABLES:")
        self.stdout.write(f"   revenue_stats.revenue_this_month: {revenue_stats['revenue_this_month']}")
        self.stdout.write(f"   order_stats.orders_today: {order_stats['orders_today']}")
        self.stdout.write(f"   product_stats.total_products: {product_stats['total_products']}")
        self.stdout.write(f"   user_stats.total_users: {user_stats['total_users']}")
        self.stdout.write(f"   category_stats.total_categories: {category_stats['total_categories']}")
        
        # Check for any potential issues
        if revenue_stats['revenue_this_month'] == 0:
            self.stdout.write(self.style.ERROR("\n❌ ISSUE: revenue_this_month is 0"))
        else:
            self.stdout.write(self.style.SUCCESS(f"\n✅ revenue_this_month should show: PKR {revenue_stats['revenue_this_month']}"))
        
        if order_stats['orders_today'] == 0:
            self.stdout.write(self.style.ERROR("❌ ISSUE: orders_today is 0"))
        else:
            self.stdout.write(self.style.SUCCESS(f"✅ orders_today should show: {order_stats['orders_today']}"))
