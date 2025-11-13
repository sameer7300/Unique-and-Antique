"""
Automatic inventory management command for non-IT administrators
This command can be run daily to send automatic low stock alerts
"""

from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from apps.products.models import Product
from apps.accounts.models import User


class Command(BaseCommand):
    help = '🤖 Automatically check inventory and send alerts to administrators'

    def add_arguments(self, parser):
        parser.add_argument(
            '--send-email',
            action='store_true',
            help='Send email alerts to administrators',
        )
        parser.add_argument(
            '--threshold',
            type=int,
            default=10,
            help='Stock threshold for alerts (default: 10)',
        )

    def handle(self, *args, **options):
        """Main command logic"""
        
        threshold = options['threshold']
        send_email = options['send_email']
        
        self.stdout.write(
            self.style.SUCCESS(f'🔍 Checking inventory levels (threshold: {threshold})...')
        )
        
        # Find low stock products
        low_stock_products = Product.objects.filter(
            stock__lte=threshold,
            track_inventory=True,
            status='active'
        ).order_by('stock')
        
        if not low_stock_products.exists():
            self.stdout.write(
                self.style.SUCCESS('✅ All products have sufficient stock levels!')
            )
            return
        
        # Display low stock products
        self.stdout.write(
            self.style.WARNING(f'⚠️ Found {low_stock_products.count()} products with low stock:')
        )
        
        for product in low_stock_products:
            status_icon = '🔴' if product.stock == 0 else '🟡'
            self.stdout.write(
                f'  {status_icon} {product.title}: {product.stock} units (SKU: {product.sku})'
            )
        
        # Send email alerts if requested
        if send_email:
            self.send_email_alerts(low_stock_products)
        
        # Auto-update product status for out-of-stock items
        out_of_stock = low_stock_products.filter(stock=0)
        if out_of_stock.exists():
            self.stdout.write(
                self.style.WARNING(f'🔄 Auto-hiding {out_of_stock.count()} out-of-stock products...')
            )
            out_of_stock.update(status='inactive')
            
        self.stdout.write(
            self.style.SUCCESS('✅ Inventory check completed!')
        )

    def send_email_alerts(self, low_stock_products):
        """Send email alerts to administrators"""
        
        try:
            # Get admin users
            admin_users = User.objects.filter(is_staff=True, is_active=True)
            
            if not admin_users.exists():
                self.stdout.write(
                    self.style.WARNING('⚠️ No admin users found to send alerts to')
                )
                return
            
            # Prepare email context
            context = {
                'low_stock_products': low_stock_products,
                'total_count': low_stock_products.count(),
                'out_of_stock_count': low_stock_products.filter(stock=0).count(),
            }
            
            # Render email content
            subject = f'🚨 Low Stock Alert - {low_stock_products.count()} Products Need Attention'
            message = render_to_string('admin/emails/low_stock_alert.txt', context)
            html_message = render_to_string('admin/emails/low_stock_alert.html', context)
            
            # Send to all admin users
            admin_emails = [user.email for user in admin_users if user.email]
            
            if admin_emails:
                send_mail(
                    subject=subject,
                    message=message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=admin_emails,
                    html_message=html_message,
                    fail_silently=False,
                )
                
                self.stdout.write(
                    self.style.SUCCESS(f'📧 Email alerts sent to {len(admin_emails)} administrators')
                )
            else:
                self.stdout.write(
                    self.style.WARNING('⚠️ No admin email addresses found')
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Failed to send email alerts: {str(e)}')
            )
