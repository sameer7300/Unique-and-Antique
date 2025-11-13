#!/usr/bin/env python
"""
Debug script to check revenue calculation issues in production.
Run this script in your production environment to diagnose the problem.
"""

import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.db.models import Sum, Count
from apps.orders.models import Order
from decimal import Decimal

def debug_revenue():
    print("🔍 REVENUE DEBUG REPORT")
    print("=" * 50)
    
    # 1. Check total orders
    total_orders = Order.objects.count()
    print(f"📊 Total Orders: {total_orders}")
    
    if total_orders == 0:
        print("❌ No orders found in database!")
        return
    
    # 2. Check order statuses
    print("\n📋 ORDER STATUS BREAKDOWN:")
    statuses = Order.objects.values('status').annotate(count=Count('id')).order_by('status')
    for status in statuses:
        print(f"   {status['status']}: {status['count']} orders")
    
    # 3. Check payment statuses
    print("\n💳 PAYMENT STATUS BREAKDOWN:")
    payment_statuses = Order.objects.values('payment_status').annotate(count=Count('id')).order_by('payment_status')
    for payment_status in payment_statuses:
        print(f"   {payment_status['payment_status']}: {payment_status['count']} orders")
    
    # 4. Check revenue calculation (current logic)
    print("\n💰 REVENUE CALCULATION (payment_status='paid'):")
    paid_orders = Order.objects.filter(payment_status='paid')
    paid_count = paid_orders.count()
    total_revenue = paid_orders.aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')
    print(f"   Orders with payment_status='paid': {paid_count}")
    print(f"   Total Revenue: PKR {total_revenue}")
    
    # 5. Check what revenue would be with different statuses
    print("\n🔄 ALTERNATIVE REVENUE CALCULATIONS:")
    
    # Check confirmed orders
    confirmed_orders = Order.objects.filter(status='confirmed')
    confirmed_count = confirmed_orders.count()
    confirmed_revenue = confirmed_orders.aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')
    print(f"   Orders with status='confirmed': {confirmed_count}")
    print(f"   Revenue if using confirmed orders: PKR {confirmed_revenue}")
    
    # Check delivered orders
    delivered_orders = Order.objects.filter(status='delivered')
    delivered_count = delivered_orders.count()
    delivered_revenue = delivered_orders.aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')
    print(f"   Orders with status='delivered': {delivered_count}")
    print(f"   Revenue if using delivered orders: PKR {delivered_revenue}")
    
    # 6. Show sample orders for debugging
    print("\n📝 SAMPLE ORDERS (first 5):")
    sample_orders = Order.objects.all()[:5]
    for order in sample_orders:
        print(f"   Order #{order.order_number}:")
        print(f"     Status: {order.status}")
        print(f"     Payment Status: {order.payment_status}")
        print(f"     Total Amount: PKR {order.total_amount}")
        print(f"     Created: {order.created_at}")
        print()
    
    # 7. Recommendations
    print("🎯 RECOMMENDATIONS:")
    if paid_count == 0 and confirmed_count > 0:
        print("   ❗ Issue found: You have confirmed orders but no 'paid' orders")
        print("   ✅ Solution: Update payment_status to 'paid' for confirmed orders")
        print("   📝 SQL Command:")
        print("      UPDATE orders_order SET payment_status='paid' WHERE status='confirmed';")
    elif paid_count == 0 and total_orders > 0:
        print("   ❗ Issue found: No orders have payment_status='paid'")
        print("   ✅ Solution: Update payment_status for your orders")
    elif paid_count > 0:
        print("   ✅ Revenue calculation should be working correctly")
        print("   🔄 Try refreshing your admin dashboard or clearing cache")

if __name__ == "__main__":
    debug_revenue()
