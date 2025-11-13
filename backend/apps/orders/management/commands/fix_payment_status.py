from django.core.management.base import BaseCommand
from django.db.models import Sum
from apps.orders.models import Order


class Command(BaseCommand):
    help = 'Fix payment status for confirmed orders'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be updated without making changes',
        )

    def handle(self, *args, **options):
        self.stdout.write("🔧 FIXING PAYMENT STATUS FOR CONFIRMED ORDERS")
        self.stdout.write("=" * 50)
        
        # Find confirmed orders with pending payment
        orders_to_fix = Order.objects.filter(
            status='confirmed',
            payment_status='pending'
        )
        
        count = orders_to_fix.count()
        self.stdout.write(f"📊 Found {count} confirmed orders with pending payment status")
        
        if count == 0:
            self.stdout.write(self.style.SUCCESS("✅ No orders need fixing!"))
            return
        
        # Show orders that will be updated
        self.stdout.write("\n📝 Orders to be updated:")
        for order in orders_to_fix[:10]:  # Show first 10
            self.stdout.write(f"   Order #{order.order_number} - PKR {order.total_amount}")
        
        if count > 10:
            self.stdout.write(f"   ... and {count - 10} more orders")
        
        # Calculate potential revenue
        potential_revenue = orders_to_fix.aggregate(total=Sum('total_amount'))['total'] or 0
        self.stdout.write(f"\n💰 Potential revenue to be recognized: PKR {potential_revenue}")
        
        if options['dry_run']:
            self.stdout.write(self.style.WARNING("\n🔍 DRY RUN - No changes made"))
            return
        
        # Update the orders
        updated = orders_to_fix.update(payment_status='paid')
        self.stdout.write(self.style.SUCCESS(f"\n✅ Updated {updated} orders successfully!"))
        
        # Calculate new total revenue
        total_revenue = Order.objects.filter(payment_status='paid').aggregate(
            total=Sum('total_amount')
        )['total'] or 0
        
        self.stdout.write(self.style.SUCCESS(f"💰 New total revenue: PKR {total_revenue}"))
