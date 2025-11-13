#!/usr/bin/env python
"""
Fix payment status for confirmed orders.
Run this script in your production environment to fix payment statuses.
"""

import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from apps.orders.models import Order

def fix_payment_status():
    print("🔧 FIXING PAYMENT STATUS FOR CONFIRMED ORDERS")
    print("=" * 50)
    
    # Find confirmed orders with pending payment
    orders_to_fix = Order.objects.filter(
        status='confirmed',
        payment_status='pending'
    )
    
    count = orders_to_fix.count()
    print(f"📊 Found {count} confirmed orders with pending payment status")
    
    if count == 0:
        print("✅ No orders need fixing!")
        return
    
    # Show orders that will be updated
    print("\n📝 Orders to be updated:")
    for order in orders_to_fix[:10]:  # Show first 10
        print(f"   Order #{order.order_number} - PKR {order.total_amount}")
    
    if count > 10:
        print(f"   ... and {count - 10} more orders")
    
    # Ask for confirmation
    response = input(f"\n❓ Update payment_status to 'paid' for {count} orders? (y/N): ")
    
    if response.lower() == 'y':
        # Update the orders
        updated = orders_to_fix.update(payment_status='paid')
        print(f"✅ Updated {updated} orders successfully!")
        
        # Calculate new revenue
        from django.db.models import Sum
        total_revenue = Order.objects.filter(payment_status='paid').aggregate(
            total=Sum('total_amount')
        )['total'] or 0
        
        print(f"💰 New total revenue: PKR {total_revenue}")
    else:
        print("❌ Operation cancelled")

if __name__ == "__main__":
    fix_payment_status()
