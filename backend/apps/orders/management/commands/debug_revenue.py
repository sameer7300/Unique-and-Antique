from django.core.management.base import BaseCommand
from django.db.models import Sum, Count
from apps.orders.models import Order
from decimal import Decimal


class Command(BaseCommand):
    help = 'Debug revenue calculation issues'

    def handle(self, *args, **options):
        self.stdout.write("🔍 REVENUE DEBUG REPORT")
        self.stdout.write("=" * 50)
        
        # 1. Check total orders
        total_orders = Order.objects.count()
        self.stdout.write(f"📊 Total Orders: {total_orders}")
        
        if total_orders == 0:
            self.stdout.write(self.style.ERROR("❌ No orders found in database!"))
            return
        
        # 2. Check order statuses
        self.stdout.write("\n📋 ORDER STATUS BREAKDOWN:")
        statuses = Order.objects.values('status').annotate(count=Count('id')).order_by('status')
        for status in statuses:
            self.stdout.write(f"   {status['status']}: {status['count']} orders")
        
        # 3. Check payment statuses
        self.stdout.write("\n💳 PAYMENT STATUS BREAKDOWN:")
        payment_statuses = Order.objects.values('payment_status').annotate(count=Count('id')).order_by('payment_status')
        for payment_status in payment_statuses:
            self.stdout.write(f"   {payment_status['payment_status']}: {payment_status['count']} orders")
        
        # 4. Check revenue calculation (current logic)
        self.stdout.write("\n💰 REVENUE CALCULATION (payment_status='paid'):")
        paid_orders = Order.objects.filter(payment_status='paid')
        paid_count = paid_orders.count()
        total_revenue = paid_orders.aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')
        self.stdout.write(f"   Orders with payment_status='paid': {paid_count}")
        self.stdout.write(f"   Total Revenue: PKR {total_revenue}")
        
        # 5. Check what revenue would be with different statuses
        self.stdout.write("\n🔄 ALTERNATIVE REVENUE CALCULATIONS:")
        
        # Check confirmed orders
        confirmed_orders = Order.objects.filter(status='confirmed')
        confirmed_count = confirmed_orders.count()
        confirmed_revenue = confirmed_orders.aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')
        self.stdout.write(f"   Orders with status='confirmed': {confirmed_count}")
        self.stdout.write(f"   Revenue if using confirmed orders: PKR {confirmed_revenue}")
        
        # Check delivered orders
        delivered_orders = Order.objects.filter(status='delivered')
        delivered_count = delivered_orders.count()
        delivered_revenue = delivered_orders.aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')
        self.stdout.write(f"   Orders with status='delivered': {delivered_count}")
        self.stdout.write(f"   Revenue if using delivered orders: PKR {delivered_revenue}")
        
        # 6. Show sample orders for debugging
        self.stdout.write("\n📝 SAMPLE ORDERS (first 5):")
        sample_orders = Order.objects.all()[:5]
        for order in sample_orders:
            self.stdout.write(f"   Order #{order.order_number}:")
            self.stdout.write(f"     Status: {order.status}")
            self.stdout.write(f"     Payment Status: {order.payment_status}")
            self.stdout.write(f"     Total Amount: PKR {order.total_amount}")
            self.stdout.write(f"     Created: {order.created_at}")
            self.stdout.write("")
        
        # 7. Recommendations
        self.stdout.write("🎯 RECOMMENDATIONS:")
        if paid_count == 0 and confirmed_count > 0:
            self.stdout.write(self.style.WARNING("   ❗ Issue found: You have confirmed orders but no 'paid' orders"))
            self.stdout.write(self.style.SUCCESS("   ✅ Solution: Update payment_status to 'paid' for confirmed orders"))
            self.stdout.write("   📝 Run this command:")
            self.stdout.write("      ./manage.py fix_payment_status")
        elif paid_count == 0 and total_orders > 0:
            self.stdout.write(self.style.WARNING("   ❗ Issue found: No orders have payment_status='paid'"))
            self.stdout.write(self.style.SUCCESS("   ✅ Solution: Update payment_status for your orders"))
        elif paid_count > 0:
            self.stdout.write(self.style.SUCCESS("   ✅ Revenue calculation should be working correctly"))
            self.stdout.write("   🔄 Try refreshing your admin dashboard or clearing cache")
