from django.core.management.base import BaseCommand
from django.conf import settings
from django.utils import timezone
from django.db import connection
from datetime import timedelta
from apps.orders.models import Order
from django.db.models import Sum
import sys
import os


class Command(BaseCommand):
    help = 'Diagnose environment differences between local and production'

    def handle(self, *args, **options):
        self.stdout.write("🔍 ENVIRONMENT DIAGNOSTIC REPORT")
        self.stdout.write("=" * 60)
        
        # 1. Basic Environment Info
        self.stdout.write("\n🖥️ ENVIRONMENT INFO:")
        self.stdout.write(f"   Python Version: {sys.version}")
        self.stdout.write(f"   Django Version: {settings.DJANGO_VERSION if hasattr(settings, 'DJANGO_VERSION') else 'Unknown'}")
        self.stdout.write(f"   Debug Mode: {settings.DEBUG}")
        self.stdout.write(f"   Database Engine: {settings.DATABASES['default']['ENGINE']}")
        self.stdout.write(f"   Database Name: {settings.DATABASES['default']['NAME']}")
        
        # 2. Timezone Info
        self.stdout.write(f"\n🕐 TIMEZONE INFO:")
        self.stdout.write(f"   Django TIME_ZONE: {settings.TIME_ZONE}")
        self.stdout.write(f"   Django USE_TZ: {settings.USE_TZ}")
        self.stdout.write(f"   Current timezone: {timezone.get_current_timezone()}")
        self.stdout.write(f"   Current datetime: {timezone.now()}")
        self.stdout.write(f"   Current date: {timezone.now().date()}")
        
        # 3. Database Connection Test
        self.stdout.write(f"\n🗄️ DATABASE CONNECTION:")
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT version()")
                db_version = cursor.fetchone()[0] if cursor.fetchone() else "Unknown"
                self.stdout.write(f"   Database Version: {db_version}")
        except Exception as e:
            self.stdout.write(f"   Database Error: {e}")
        
        # 4. Order Model Test
        self.stdout.write(f"\n📦 ORDER MODEL TEST:")
        try:
            total_orders = Order.objects.count()
            self.stdout.write(f"   Total Orders: {total_orders}")
            
            if total_orders > 0:
                # Show first order details
                first_order = Order.objects.first()
                self.stdout.write(f"   First Order:")
                self.stdout.write(f"     ID: {first_order.id}")
                self.stdout.write(f"     Number: {first_order.order_number}")
                self.stdout.write(f"     Status: {first_order.status}")
                self.stdout.write(f"     Payment Status: {first_order.payment_status}")
                self.stdout.write(f"     Total Amount: {first_order.total_amount}")
                self.stdout.write(f"     Created At: {first_order.created_at}")
                self.stdout.write(f"     Created At (date): {first_order.created_at.date()}")
                
                # Test the exact revenue query
                today = timezone.now().date()
                self.stdout.write(f"\n💰 REVENUE QUERY TEST (Today: {today}):")
                
                # Raw SQL test
                with connection.cursor() as cursor:
                    cursor.execute("""
                        SELECT SUM(total_amount) 
                        FROM orders_order 
                        WHERE payment_status = 'paid'
                    """)
                    raw_total = cursor.fetchone()[0] or 0
                    self.stdout.write(f"   Raw SQL Total Revenue: {raw_total}")
                    
                    cursor.execute("""
                        SELECT SUM(total_amount) 
                        FROM orders_order 
                        WHERE payment_status = 'paid' 
                        AND DATE(created_at) >= %s
                    """, [today - timedelta(days=30)])
                    raw_month = cursor.fetchone()[0] or 0
                    self.stdout.write(f"   Raw SQL Month Revenue: {raw_month}")
                
                # Django ORM test
                orm_total = Order.objects.filter(payment_status='paid').aggregate(
                    total=Sum('total_amount'))['total'] or 0
                self.stdout.write(f"   ORM Total Revenue: {orm_total}")
                
                month_ago = today - timedelta(days=30)
                orm_month = Order.objects.filter(
                    created_at__date__gte=month_ago,
                    payment_status='paid'
                ).aggregate(total=Sum('total_amount'))['total'] or 0
                self.stdout.write(f"   ORM Month Revenue: {orm_month}")
                
        except Exception as e:
            self.stdout.write(f"   Order Model Error: {e}")
        
        # 5. Settings Comparison
        self.stdout.write(f"\n⚙️ RELEVANT SETTINGS:")
        relevant_settings = [
            'DEBUG', 'ALLOWED_HOSTS', 'TIME_ZONE', 'USE_TZ', 'USE_I18N', 'USE_L10N',
            'STATIC_URL', 'MEDIA_URL', 'SECRET_KEY'
        ]
        
        for setting_name in relevant_settings:
            if hasattr(settings, setting_name):
                value = getattr(settings, setting_name)
                if setting_name == 'SECRET_KEY':
                    value = f"{value[:10]}..." if value else "Not set"
                self.stdout.write(f"   {setting_name}: {value}")
        
        # 6. Cache Settings
        self.stdout.write(f"\n🗂️ CACHE SETTINGS:")
        if hasattr(settings, 'CACHES'):
            for cache_name, cache_config in settings.CACHES.items():
                self.stdout.write(f"   {cache_name}: {cache_config.get('BACKEND', 'Unknown')}")
        
        # 7. Middleware Check
        self.stdout.write(f"\n🔧 MIDDLEWARE:")
        if hasattr(settings, 'MIDDLEWARE'):
            for middleware in settings.MIDDLEWARE:
                if 'cache' in middleware.lower():
                    self.stdout.write(f"   CACHE: {middleware}")
        
        # 8. Final Recommendations
        self.stdout.write(f"\n🎯 RECOMMENDATIONS:")
        if total_orders == 0:
            self.stdout.write("   ❌ No orders found - database might be empty")
        elif orm_total != raw_total:
            self.stdout.write("   ❌ ORM and Raw SQL results differ - possible ORM issue")
        elif orm_month == 0 and orm_total > 0:
            self.stdout.write("   ❌ Monthly revenue is 0 but total revenue exists - date filtering issue")
        else:
            self.stdout.write("   ✅ Revenue calculation should be working")
            self.stdout.write("   🔍 Check browser cache, web server cache, or CDN cache")
