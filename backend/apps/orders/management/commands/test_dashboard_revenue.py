from django.core.management.base import BaseCommand
from django.db.models import Sum, Count, Avg
from django.utils import timezone
from datetime import datetime, timedelta
from apps.orders.models import Order


class Command(BaseCommand):
    help = 'Test the exact revenue calculation used in dashboard'

    def handle(self, *args, **options):
        self.stdout.write("🧪 TESTING DASHBOARD REVENUE CALCULATION")
        self.stdout.write("=" * 50)
        
        # Get the same date calculations as the dashboard
        today = timezone.now().date()
        yesterday = today - timedelta(days=1)
        week_ago = today - timedelta(days=7)
        month_ago = today - timedelta(days=30)
        year_ago = today - timedelta(days=365)
        
        self.stdout.write(f"📅 Today: {today}")
        self.stdout.write(f"📅 Month ago: {month_ago}")
        
        # Test the exact queries from dashboard
        self.stdout.write("\n💰 REVENUE CALCULATIONS:")
        
        # Total Revenue
        total_revenue = Order.objects.filter(
            payment_status='paid'
        ).aggregate(total=Sum('total_amount'))['total'] or 0
        self.stdout.write(f"   Total Revenue: PKR {total_revenue}")
        
        # Revenue Today
        revenue_today = Order.objects.filter(
            created_at__date=today, 
            payment_status='paid'
        ).aggregate(total=Sum('total_amount'))['total'] or 0
        self.stdout.write(f"   Revenue Today: PKR {revenue_today}")
        
        # Revenue Yesterday
        revenue_yesterday = Order.objects.filter(
            created_at__date=yesterday, 
            payment_status='paid'
        ).aggregate(total=Sum('total_amount'))['total'] or 0
        self.stdout.write(f"   Revenue Yesterday: PKR {revenue_yesterday}")
        
        # Revenue This Week
        revenue_this_week = Order.objects.filter(
            created_at__date__gte=week_ago, 
            payment_status='paid'
        ).aggregate(total=Sum('total_amount'))['total'] or 0
        self.stdout.write(f"   Revenue This Week: PKR {revenue_this_week}")
        
        # Revenue This Month
        revenue_this_month = Order.objects.filter(
            created_at__date__gte=month_ago, 
            payment_status='paid'
        ).aggregate(total=Sum('total_amount'))['total'] or 0
        self.stdout.write(f"   Revenue This Month: PKR {revenue_this_month}")
        
        # Revenue This Year
        revenue_this_year = Order.objects.filter(
            created_at__date__gte=year_ago, 
            payment_status='paid'
        ).aggregate(total=Sum('total_amount'))['total'] or 0
        self.stdout.write(f"   Revenue This Year: PKR {revenue_this_year}")
        
        # Show orders for today specifically
        self.stdout.write(f"\n📋 ORDERS TODAY ({today}):")
        today_orders = Order.objects.filter(created_at__date=today)
        for order in today_orders:
            self.stdout.write(f"   Order #{order.order_number}:")
            self.stdout.write(f"     Status: {order.status}")
            self.stdout.write(f"     Payment Status: {order.payment_status}")
            self.stdout.write(f"     Amount: PKR {order.total_amount}")
            self.stdout.write(f"     Created: {order.created_at}")
        
        if today_orders.count() == 0:
            self.stdout.write("   No orders found for today")
        
        # Check if there are any caching issues
        self.stdout.write(f"\n🔍 CACHE CHECK:")
        self.stdout.write(f"   Current timezone: {timezone.get_current_timezone()}")
        self.stdout.write(f"   Current datetime: {timezone.now()}")
        
        # Show the exact data that should appear in dashboard
        self.stdout.write(f"\n📊 DASHBOARD SHOULD SHOW:")
        self.stdout.write(f"   💰 Revenue This Month: PKR {revenue_this_month}")
        self.stdout.write(f"   🛒 Orders Today: {Order.objects.filter(created_at__date=today).count()}")
        
        if revenue_this_month == 0:
            self.stdout.write(self.style.ERROR("\n❌ ISSUE: Revenue This Month is 0!"))
            self.stdout.write("   This suggests a timezone or date filtering issue")
        else:
            self.stdout.write(self.style.SUCCESS(f"\n✅ Revenue calculation is working: PKR {revenue_this_month}"))
